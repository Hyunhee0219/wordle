from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import get_random_word
from django.utils.safestring import mark_safe
import json
import random
import re

# 각 단어 목록의 경로를 정의
WORDLIST_PATHS = {
    'Run': 'wordle_app/static/Run.txt',
    'Start': 'wordle_app/static/Start.txt',
    'Fly': 'wordle_app/static/Fly.txt',
    'Jump': 'wordle_app/static/Jump.txt',
    'Master': 'wordle_app/static/Master.txt',
    'Walk': 'wordle_app/static/Walk.txt',
}

# 단어 목록을 변경하는 뷰 함수
@csrf_exempt  # CSRF 보호를 비활성화
def change_wordlist(request):
    if request.method == 'POST':  # 요청이 POST인 경우에만 처리
        try:
            data = json.loads(request.body)  # 요청 본문을 JSON으로 파싱
            wordlist = data.get('wordlist')  # 'wordlist' 값을 가져옴
            print(f"Requested wordlist: {wordlist}")  # 디버그 로그 출력
            if wordlist in WORDLIST_PATHS:  # 요청된 단어 목록이 유효한지 확인
                # 유효한 경우, 세션에 새로운 단어와 설정을 저장
                request.session['SECRET_WORD'] = get_random_word(wordlist)
                request.session['current_wordlist'] = wordlist
                request.session['attempts'] = 0
                request.session['history'] = []
                return JsonResponse({'message': '단어 목록이 변경되었습니다. New Game 버튼을 눌러주세요.'}, status=200)
            else:
                return JsonResponse({'error': '잘못된 단어 목록입니다.'}, status=400)
        except (ValueError, FileNotFoundError) as e:  # 예외 처리
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:  # 일반적인 예외 처리
            return JsonResponse({'error': '서버 오류가 발생했습니다.'}, status=500)
    else:
        return JsonResponse({'error': 'POST 요청이 필요합니다.'}, status=400)

# 게임의 메인 페이지를 렌더링하는 뷰 함수
def index(request):
    # 세션에 'SECRET_WORD'가 없는 경우, 초기 설정을 수행
    if 'SECRET_WORD' not in request.session:
        current_wordlist = request.session.get('current_wordlist', 'Fly')  # 기본 단어 목록 설정
        try:
            print(f"Initial wordlist: {current_wordlist}")  # 디버그 로그 출력
            request.session['SECRET_WORD'] = get_random_word(current_wordlist)  # 새로운 단어 설정
        except Exception as e:  # 예외 처리
            return render(request, 'index.html', {'response_text': str(e)})
        request.session['history'] = []  # 시도 기록 초기화
        request.session['attempts'] = 0  # 시도 횟수 초기화
        request.session.modified = True  # 세션이 수정되었음을 표시

    if request.method == 'POST':  # 요청이 POST인 경우에만 처리
        current_wordlist = request.POST.get('current_wordlist', '')  # 현재 단어 목록 가져오기
        input_text = request.POST.get('input_text', '').strip().lower()  # 입력된 텍스트 처리

        # 한글이 포함된 경우 한글을 지우고 영어 입력 요청 메시지 표시
        if re.search('[\u3131-\u3163\uac00-\ud7a3]+', input_text):
            input_text = re.sub('[\u3131-\u3163\uac00-\ud7a3]+', '', input_text)
            response_text = '영어 단어를 입력하세요.'
            return render(request, 'index.html', {
                'response_text': response_text,
                'current_wordlist': current_wordlist,
                'history': request.session.get('history', []),
                'keypad_states': json.dumps({})
            })
        
        if len(input_text) != 5:  # 입력된 텍스트가 5글자가 아닌 경우 처리
            response_text = '5글자로 입력해주세요.'
            return render(request, 'index.html', {
                'response_text': response_text,
                'current_wordlist': current_wordlist,
                'history': request.session.get('history', []),
                'keypad_states': json.dumps({})
            })

        # 세션에 시도 횟수와 기록이 없는 경우 초기화
        if 'attempts' not in request.session:
            request.session['attempts'] = 0
            request.session['history'] = []
        
        request.session['attempts'] += 1  # 시도 횟수 증가
        attempts = request.session['attempts']  # 현재 시도 횟수 가져오기

        if attempts >= 10:  # 시도 횟수가 10회를 초과한 경우 게임 오버 처리
            SECRET_WORD = request.session['SECRET_WORD']
            response_text = f'게임 오버! <br>정답은 "{SECRET_WORD}"입니다.'
            return render(request, 'index.html', {'response_text': response_text, 'current_wordlist': current_wordlist})

        SECRET_WORD = request.session['SECRET_WORD']  # 세션에서 정답 단어 가져오기

        if input_text == SECRET_WORD:  # 정답을 맞춘 경우
            response_text = '축하합니다! <br>정답이에요!'
            matched = [('green', letter) for letter in input_text]  # 모든 글자를 초록색으로 표시
            request.session['attempts'] = 0  # 시도 횟수 초기화
            request.session['history'] = []  # 시도 기록 초기화
            request.session['SECRET_WORD'] = get_random_word(current_wordlist)  # 새로운 단어 설정
        else:  # 정답을 맞추지 못한 경우
            response_text = '오답이에요. <br>'
            response_text += f'현재 {attempts}번째 기회를 사용했어요. <br>남은 기회는 {10 - attempts}번 입니다.<br>'
            matched = []
            for i in range(5):  # 입력된 단어와 정답을 비교하여 매칭 상태 설정
                if input_text[i] == SECRET_WORD[i]:
                    matched.append(('green', input_text[i]))
                elif input_text[i] in SECRET_WORD:
                    matched.append(('yellow', input_text[i]))
                else:
                    matched.append(('black', input_text[i]))

        response_text = mark_safe(response_text)  # 안전한 HTML로 마크업
        request.session['history'].append({
            'word': input_text,
            'matched': matched,
        })  # 시도 기록에 추가
        request.session.modified = True  # 세션이 수정되었음을 표시

        keypad_states = {}  # 키패드 상태 초기화
        for entry in request.session['history']:
            for color, letter in entry['matched']:
                if letter in keypad_states:
                    if keypad_states[letter] == 'green' or (keypad_states[letter] == 'yellow' and color != 'green'):
                        continue
                keypad_states[letter] = color  # 키패드 상태 설정

        return render(request, 'index.html', {
            'response_text': response_text,
            'history': request.session['history'],
            'current_wordlist': current_wordlist,
            'keypad_states': json.dumps(keypad_states)
        })
    else:
        request.session['history'] = []  # 시도 기록 초기화
        request.session['attempts'] = 0  # 시도 횟수 초기화
        return render(request, 'index.html', {
            'history': request.session['history'],
            'current_wordlist': request.session.get('current_wordlist', ''),
            'keypad_states': json.dumps({})
        })
