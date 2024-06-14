from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import get_random_word
from django.utils.safestring import mark_safe
import random
import json

# 각 단어 목록의 파일 경로
WORDLIST_PATHS = {
    'Run': 'wordle_app/static/Run.txt',
    'Start': 'wordle_app/static/Start.txt',
    'Fly': 'wordle_app/static/Fly.txt',
}

@csrf_exempt
def change_wordlist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        wordlist = data.get('wordlist')
        if wordlist in WORDLIST_PATHS:  # 요청된 단어 목록이 유효한지 확인
            try:
                with open(WORDLIST_PATHS[wordlist], 'r', encoding='utf-8') as file:
                    words = file.read().splitlines()
                # 세션에 새로운 정답 단어와 게임 상태 정보 저장
                request.session['SECRET_WORD'] = random.choice(words).strip()
                request.session['current_wordlist'] = wordlist
                request.session['attempts'] = 0
                request.session['history'] = []
                return JsonResponse({'message': '단어 목록이 변경되었습니다. New Game 버튼을 눌러주세요.'}, status=200)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': '잘못된 단어 목록입니다.'}, status=400)
    else:
        return JsonResponse({'error': 'POST 요청이 필요합니다.'}, status=400)

# 게임의 메인 페이지
def index(request):
    if 'SECRET_WORD' not in request.session:
        current_wordlist = request.session.get('current_wordlist', 'Fly')
        request.session['SECRET_WORD'] = get_random_word(current_wordlist)
        request.session['history'] = []
        request.session['attempts'] = 0
        request.session.modified = True

    if request.method == 'POST':
        current_wordlist = request.POST.get('current_wordlist', '')  # POST 요청에서 현재 단어 목록 가져오기

        input_text = request.POST.get('input_text', '').strip().lower()

        # 입력된 단어의 길이가 5글자가 아닌 경우
        if len(input_text) != 5:
            response_text = '5글자로 입력해주세요.'
            return render(request, 'index.html', {
                'response_text': response_text, 
                'current_wordlist': current_wordlist, 
                'history': request.session.get('history', []), 
                'keypad_states': json.dumps({})
            })

        if 'attempts' not in request.session:
            request.session['attempts'] = 0
            request.session['history'] = []
        request.session['attempts'] += 1
        attempts = request.session['attempts']

        # 시도 횟수가 10회 이상일 경우 게임 오버 처리
        if attempts >= 10:
            SECRET_WORD = request.session['SECRET_WORD']
            response_text = f'게임 오버! <br>정답은 "{SECRET_WORD}"입니다.'
            return render(request, 'index.html', {'response_text': response_text, 'current_wordlist': current_wordlist})

        SECRET_WORD = request.session['SECRET_WORD']
        if input_text == SECRET_WORD:   # 정답을 맞춘 경우
            response_text = '축하합니다! <br>정답이에요!'
            matched = [('green', letter) for letter in input_text]
            request.session['attempts'] = 0
            request.session['history'] = []
            request.session['SECRET_WORD'] = get_random_word(current_wordlist)
        else:   # 오답일 경우
            response_text = '오답이에요. <br>'
            response_text += f'현재 {attempts}번째 기회를 사용했어요. <br>남은 기회는 {10 - attempts}번 입니다.<br>'
            matched = []
            for i in range(5):
                if input_text[i] == SECRET_WORD[i]:
                    matched.append(('green', input_text[i]))
                elif input_text[i] in SECRET_WORD:
                    matched.append(('yellow', input_text[i]))
                else:
                    matched.append(('black', input_text[i]))

        response_text = mark_safe(response_text)

        request.session['history'].append({
            'word': input_text,
            'matched': matched,
        })
        request.session.modified = True

        # 히스토리를 바탕으로 키패드 상태 업데이트
        keypad_states = {}
        for entry in request.session['history']:
            for color, letter in entry['matched']:
                if letter in keypad_states:
                    if keypad_states[letter] == 'green' or (keypad_states[letter] == 'yellow' and color != 'green'):
                        continue
                keypad_states[letter] = color

        return render(request, 'index.html', {
            'response_text': response_text,
            'history': request.session['history'],
            'current_wordlist': current_wordlist,
            'keypad_states': json.dumps(keypad_states)
        })
    else:
        # 여기서 history와 attempts를 초기화합니다.
        request.session['history'] = []
        request.session['attempts'] = 0

        return render(request, 'index.html', {
            'history': request.session['history'],
            'current_wordlist': request.session.get('current_wordlist', ''),
            'keypad_states': json.dumps({})
        })
