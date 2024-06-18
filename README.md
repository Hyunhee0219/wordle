# Wordle Game (MilkT Elementary)

## Description
본 워들 게임은 천재교육 밀크T 수준별 영어 학습 자료를 바탕으로 제작되었으며, 사용자가 5글자의 영어 단어를 맞추는 단어 추측 게임입니다. <br>
새로운 게임마다 새로운 단어가 제공되며, 플레이어는 10번의 시도를 통해 단어를 맞춰야 합니다. <br>
각 시도 후에는 입력한 단어의 각 글자가 정답과 비교되어 다음과 같이 표시됩니다: <br>

- 🟩 : 위치와 글자가 모두 맞습니다.
- 🟨 : 글자는 맞지만 위치가 틀립니다.
- ⬛ : 글자와 위치가 모두 틀립니다.
  
플레이어는 이러한 힌트를 바탕으로 단어를 추측해 나가야 합니다.<br>
10 번의 시도 내에 단어를 맞추면 승리하고, 맞추지 못하면 패배하게 됩니다.<br>
이 게임은 수준별 영단어 어휘력 향상과 자기주도학습 능력을 키우는 데 도움이 됩니다.<br>

## How to start the game
1. pip install django
2. pip install django-admin ( C++ error : https://visualstudio.microsoft.com/ko/visual-cpp-build-tools/ 에서 C++ runtime 설치)
3. cd 파일 경로 (ex. C:\Users\user\Desktop\django_test\django_test\wordle_project)
4. python manage.py runserver
5. http://127.0.0.1:8000/ 링크 접속

## How to play Wordle
1. Rule 버튼을 눌러 규칙을 확인한다.
2. 자신의 수준에 맞는 단어 단계를 고른다.
3. 5글자 단어를 입력한다. 이때 위치와 글자가 모두 맞으면 초록색, 글자는 맞지만 위치가 틀리면 노란색, 글자와 위치가 모두 틀리면 검정새으로 키패드가 바뀐다.
4. 힌트를 이용하여 10번안에 정답 단어를 맞춘다.
5. 이후 영어 사전 혹은 밀크T 사이트에 접속하여 추가적인 검색 및 학습을 진행한다.
6. 새로운 게임을 반복하여 영단어를 학습한다.

## Team
천재교육 빅데이터 8기 박지석<br>
천재교육 빅데이터 8기 이수민<br>
천재교육 빅데이터 8기 이현희<br>
