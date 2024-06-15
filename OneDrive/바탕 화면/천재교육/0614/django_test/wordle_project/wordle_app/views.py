from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import get_random_word
from django.utils.safestring import mark_safe
import json
import random

WORDLIST_PATHS = {
    'Run': 'wordle_app/static/Run.txt',
    'Start': 'wordle_app/static/Start.txt',
    'Fly': 'wordle_app/static/Fly.txt',
    'Jump': 'wordle_app/static/Jump.txt',
    'Master': 'wordle_app/static/Master.txt',
    'Walk': 'wordle_app/static/Walk.txt',
}

@csrf_exempt
def change_wordlist(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            wordlist = data.get('wordlist')
            print(f"Requested wordlist: {wordlist}")  # Debug log
            if wordlist in WORDLIST_PATHS:
                request.session['SECRET_WORD'] = get_random_word(wordlist)
                request.session['current_wordlist'] = wordlist
                request.session['attempts'] = 0
                request.session['history'] = []
                return JsonResponse({'message': '단어 목록이 변경되었습니다. New Game 버튼을 눌러주세요.'}, status=200)
            else:
                return JsonResponse({'error': '잘못된 단어 목록입니다.'}, status=400)
        except (ValueError, FileNotFoundError) as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': '서버 오류가 발생했습니다.'}, status=500)
    else:
        return JsonResponse({'error': 'POST 요청이 필요합니다.'}, status=400)

def index(request):
    if 'SECRET_WORD' not in request.session:
        current_wordlist = request.session.get('current_wordlist', 'Fly')
        try:
            print(f"Initial wordlist: {current_wordlist}")  # Debug log
            request.session['SECRET_WORD'] = get_random_word(current_wordlist)
        except Exception as e:
            return render(request, 'index.html', {'response_text': str(e)})
        request.session['history'] = []
        request.session['attempts'] = 0
        request.session.modified = True

    if request.method == 'POST':
        current_wordlist = request.POST.get('current_wordlist', '')  
        input_text = request.POST.get('input_text', '').strip().lower()

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

        if attempts >= 10:
            SECRET_WORD = request.session['SECRET_WORD']
            response_text = f'게임 오버! <br>정답은 "{SECRET_WORD}"입니다.'
            return render(request, 'index.html', {'response_text': response_text, 'current_wordlist': current_wordlist})

        SECRET_WORD = request.session['SECRET_WORD']
        if input_text == SECRET_WORD:
            response_text = '축하합니다! <br>정답이에요!'
            matched = [('green', letter) for letter in input_text]
            request.session['attempts'] = 0
            request.session['history'] = []
            request.session['SECRET_WORD'] = get_random_word(current_wordlist)
        else:
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
        request.session['history'] = []
        request.session['attempts'] = 0

        return render(request, 'index.html', {
            'history': request.session['history'],
            'current_wordlist': request.session.get('current_wordlist', ''),
            'keypad_states': json.dumps({})
        })
