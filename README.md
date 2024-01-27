## SNAPHOT Voting_Async

## config.py


TIME - Время между запросами 1 адреса
TIMEMAX - рандомизирует время от 1 до TIMEMAX, что бы добавить чутка рандома между разными аккаунтами
USE_PROXY - True, если используете проски; False, если не используете прокси
TIME_ERROR - время ожидания после ошибки
RANDOM_CHOICES = True, если надо случайным образом выбирать как голосовать. False, если надо задать один голосо за все акки
VOTE_CHOICES - вписываем в скобки [1, 2, 3] порядковый номер опций, из которых случайным образом будет вибраться голос YES, NO или Abstain

Как заполнять типы голосов:
1. Если надо задать один тип голоса (например, YES) на все акки

```
RANDOM_CHOICES = False
VOTE_CHOICES = 1
```

2. Если надо случайным образом выбирать тип голоса из YES, NO, ABSTAIN, то ставим
```
RANDOM_CHOICES = True
VOTE_CHOICES = [1, 2, 3]
```

3.1 Если в proposal можно выбрать > 1 голоса:

```
RANDOM_CHOICES = False
VOTE_CHOICES = [1, 2]
```
![image](https://user-images.githubusercontent.com/117441696/212177066-ca0c2746-34d5-44ed-9ede-1efb85480e03.png)

3.2 Если в proposal нужно выбрать голос и внутри него выбрать меру:

```
{"1":1}
{"CHOISE":NUM_VOTE}
```
![image](https://user-images.githubusercontent.com/117441696/227935482-243d8ec8-0d9a-4bd7-8080-982d5868e27a.png)


## data.txt
Пробегаетеь по всем proposal и собираете информацию

```
space@proposal
space@proposal
```

## proxy.txt

Прокси в формате:
```
username:password@ip:port
username:password@ip:port
```
Если используете один прокси на все акк ,продублируйте его ,что бы прокси было >= key

## key.txt

Вставлеяете свои приватные ключи

---------------------------------------------------------------------

Если появляется ошибка: (TypeError: Object of type bytes is not JSON serializable)
```
pip install web3==6.0.0b7 
pip install eth_account==0.7.0
pip install tqdm
pip install loguru
```
