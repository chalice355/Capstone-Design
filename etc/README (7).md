# 셸변수와 환경변수의 차이점을 설명하라.
| 구분 | 셸변수 | 환경변수 |
| --- | --- | --- |
| 의미 | 셸 내부에서 사용하는 변수, 숫자나 문자열 등 셸의 특성값을 저장 | 셸변수 중 외부 명령어에서도 참조할 수 있도록 설정된 변수 |
| 참조 범위 | 현재 셸 프로세스 안에서만 사용 가능 (내장 명령어만 참조) | 현재 셸 + 셸에서 실행한 외부 명령어(자식 프로세스)에서도 참조 가능 |
| 설정 방법 | `변수명=값` | `export 변수명=값` 또는 셸변수를 만든 뒤 `export 변수명` |
| 목록 확인 | `set` (셸변수와 환경변수 모두 출력) | `printenv` 또는 `env` |
| 예 | PS1 | PATH, LANG, HOME, SHELL |

- 배시셸과 외부 명령어(cp, cat 등)는 각각 독립된 프로세스이므로 서로의 메모리 공간에 접근할 수 없음
- 그래서 외부 명령어는 셸변수를 읽을 수 없고, export로 환경변수로 지정한 변수만 복사되어 전달됨
- 예를 들어 LANG은 환경변수이므로 외부 명령어 cat이 LANG 값을 참조하여 도움말을 한글 또는 영어로 출력함

```bash
$ MYVAR=hello            # 셸변수 선언
$ echo $MYVAR            # 셸 안에서는 참조 가능
hello
$ bash -c 'echo $MYVAR'  # 새로 실행한 bash(외부 프로세스)에서는 참조 불가
                         # 빈 줄 출력
$ export MYVAR           # 환경변수로 설정
$ bash -c 'echo $MYVAR'  # 외부 프로세스에서도 참조 가능
hello
```

<img src="img8-1-1.png">

# 환경변수 PS1, PATH, SHELL, LANG을 출력하고 기능을 설명하라.
```bash
$ echo $PS1
$ echo $PATH
$ echo $SHELL
$ echo $LANG
```
| 변수 | 출력 예 | 기능 |
| --- | --- | --- |
| PS1 | `\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\u@\h:\w\$` | 프롬프트 문자열을 정의, \u는 사용자 이름, \h는 호스트 이름, \w는 현재 작업 디렉터리를 의미하며 값을 바꾸면 프롬프트 모양이 바뀜 |
| PATH | `/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:...` | 명령어 실행파일을 찾을 디렉터리 목록, 콜론(:)으로 구분하며 셸은 이 디렉터리들에서 명령어를 찾음 |
| SHELL | `/bin/bash` | 현재 사용자의 로그인 셸 실행파일 경로 |
| LANG | `C.UTF-8` 또는 `ko_KR.UTF-8` | 로케일(언어_지역.문자인코딩) 설정, 명령어의 메시지 언어, 날짜 표시 방식 등이 이 값에 따라 바뀜 |

- 참고 : PS1은 .bashrc에서 export 없이 설정되므로 엄밀히는 셸변수임, `echo $PS1`로는 출력되지만 `printenv PS1`로는 출력되지 않음
- PATH, SHELL, LANG은 `printenv PATH SHELL LANG`으로도 출력되는 환경변수

<img src="img8-1-2.png">

# 셸이 명령어 파일의 위치를 어떻게 찾는지 설명하라.
1. 명령어를 입력하면 셸은 먼저 그 명령어가 alias(별칭)인지, 셸 내장 명령어(cd, pwd, set 등)인지 확인하고, 해당하면 셸 안에서 바로 실행함
2. 외부 명령어이면 환경변수 PATH에 콜론(:)으로 구분되어 저장된 디렉터리를 앞에서부터 차례대로 검색함
3. 처음 발견된 실행파일을 실행하고, 모든 디렉터리에서 찾지 못하면 `command not found` 에러를 출력함
4. 명령어를 /bin/ls처럼 절대경로나 ./myprog처럼 경로를 포함하여 입력하면 PATH를 검색하지 않고 그 경로의 파일을 바로 실행함
5. 보안 때문에 현재 작업 디렉터리는 PATH에 포함되어 있지 않으므로, 현재 디렉터리의 프로그램은 ./를 붙여 실행해야 함

```bash
$ type cd         # cd is a shell builtin (내장 명령어)
$ type ls         # ls is aliased to `ls --color=auto' (alias)
$ which ls        # /usr/bin/ls (PATH에서 찾은 실행파일 경로)
$ echo $PATH      # 셸이 검색하는 디렉터리 목록
```

<img src="img8-1-3.png">

# 셸스크립트를 설명하라.
- 여러 개의 명령어를 텍스트 파일에 작성해 두고 한 번에 실행할 수 있도록 만든 파일
- 셸이 파일에 적힌 명령어를 위에서부터 한 줄씩 읽어서 실행함
- 반복되는 작업을 자동화할 때 사용하며, 변수, 조건문(if), 반복문(for, while) 등도 사용 가능
- .bashrc, .profile, /etc/profile도 셸이 실행될 때 자동으로 실행되는 셸스크립트임
- 보통 확장자는 .sh를 사용하고, 첫 줄에 `#!/bin/bash`(셔뱅)를 써서 이 파일을 실행할 셸을 지정함

## 소스파일 hello.sh
```bash
#!/bin/bash
# 간단한 셸스크립트 예제
echo "hello $USER"
echo "현재 작업 디렉터리 : $(pwd)"
date
```
| 라인 | 코드 | 설명 |
| --- | --- | --- |
| 1 | `#!/bin/bash` | 셔뱅(shebang), 이 스크립트를 /bin/bash로 실행하라는 의미 |
| 2 | `# 간단한 셸스크립트 예제` | #으로 시작하는 줄은 주석 |
| 3 | `echo "hello $USER"` | 환경변수 USER(사용자 이름)를 참조하여 인사말 출력 |
| 4 | `echo "현재 작업 디렉터리 : $(pwd)"` | $(명령어)는 명령어 치환, pwd의 실행결과를 문자열에 넣어 출력 |
| 5 | `date` | 현재 날짜와 시각 출력 |

# 셸스크립트의 실행방법 3가지를 조사하라.
| 방법 | 명령어 | 설명 |
| --- | --- | --- |
| 1. bash 명령어의 인자로 실행 | `$ bash hello.sh` | 새로운 bash 프로세스(자식 셸)를 실행하여 스크립트를 읽어 실행, 실행 권한이 없어도 됨 |
| 2. 실행 권한을 주고 경로로 실행 | `$ chmod +x hello.sh`<br>`$ ./hello.sh` | 파일에 실행 권한을 부여한 뒤 경로를 지정하여 실행, 첫 줄의 #!/bin/bash로 지정한 셸이 자식 프로세스로 실행됨, 현재 디렉터리는 PATH에 없으므로 ./를 붙여야 함 |
| 3. source 명령어로 실행 | `$ source hello.sh`<br>`$ . hello.sh` | 새 프로세스를 만들지 않고 **현재 셸**에서 스크립트를 실행, 스크립트에서 설정한 변수가 현재 셸에 그대로 남으므로 .bashrc 수정 내용을 반영할 때 사용 |

- 1, 2번은 자식 셸에서 실행되므로 스크립트 안에서 선언한 변수나 cd로 이동한 결과가 실행이 끝나면 사라짐
- 3번은 현재 셸에서 실행되므로 변수와 작업 디렉터리 변경이 그대로 유지됨

<img src="img8-1-4.png">

# .bashrc 파일에 환경변수 MYVER을 선언하고 값을 ubuntu 26.04로 설정하는 코드를 추가하고 .bashrc 파일을 다시 실행(source)하라. 그리고 환경변수 MYVER의 값이 잘 설정되었는지 명령어(echo)로 확인하라
## 실행 명령어
```bash
$ cp ~/.bashrc ~/.bashrc.org
$ vi ~/.bashrc
$ source ~/.bashrc
$ echo $MYVER
ubuntu 26.04
$ printenv MYVER
ubuntu 26.04
```
| 명령어 | 설명 |
| --- | --- |
| `cp ~/.bashrc ~/.bashrc.org` | 수정하기 전에 .bashrc를 백업, 잘못 수정해도 복원 가능 |
| `vi ~/.bashrc` | vi 에디터로 .bashrc를 열고 `G`로 파일 마지막으로 이동, `o`로 아래에 새 줄을 열어 코드 추가 후 `ESC` → `:wq`로 저장 및 종료 |
| `source ~/.bashrc` | 셸을 종료하지 않고 현재 셸에서 .bashrc를 다시 실행하여 수정 내용을 반영 |
| `echo $MYVER` | 환경변수 MYVER의 값 출력 |
| `printenv MYVER` | 환경변수 목록에 MYVER가 있는지 확인, export했으므로 출력됨 |

## .bashrc 마지막에 추가한 코드
```bash
# 환경변수 MYVER 설정
export MYVER="ubuntu 26.04"
```
| 라인 | 코드 | 설명 |
| --- | --- | --- |
| 1 | `# 환경변수 MYVER 설정` | 주석 |
| 2 | `export MYVER="ubuntu 26.04"` | 셸변수 MYVER에 값을 저장하고 export로 환경변수로 설정, 값에 공백이 있으므로 큰따옴표로 감싸야 함, = 양옆에 공백을 넣으면 안 됨 |

- 따옴표 없이 `export MYVER=ubuntu 26.04`라고 쓰면 MYVER에는 ubuntu만 저장되고 26.04는 별도의 변수 이름으로 해석되어 `not a valid identifier` 에러 발생

<img src="img8-1-5.png">

# 환경변수에 경로를 추가할 때 $ PATH='$PATH:~/bin' 처럼 작성하면 어떻게 되는지 설명하라.
```bash
$ PATH='$PATH:~/bin'
$ echo $PATH
$PATH:~/bin
$ ls
bash: ls: command not found
```
- 작은따옴표 안의 모든 특수 기호는 무시되므로 $PATH가 기존 PATH 값으로 치환되지 않음
- 따라서 PATH에 `$PATH:~/bin`이라는 글자 그대로의 문자열이 저장되어 기존 경로(/usr/bin, /bin 등)가 모두 사라짐
- 셸은 `$PATH`와 `~/bin`이라는 이름의 디렉터리에서만 명령어를 찾게 되므로, ls, cat 같은 외부 명령어를 찾지 못해 `command not found` 에러가 발생함
- cd, echo 같은 내장 명령어는 PATH와 관계없이 실행됨
- 올바른 방법은 큰따옴표를 사용하여 `PATH="$PATH:~/bin"`으로 작성하는 것, 큰따옴표 안에서는 변수 치환이 적용되어 기존 PATH 뒤에 ~/bin이 추가됨
- 잘못 설정했을 때는 터미널을 닫고 다시 열면 원래 PATH로 복구됨 (PATH 변경은 현재 셸에만 적용되었기 때문)

<img src="img8-1-6.png">
