# .gitignore -> 깃에 올릴 때 제외하고 싶은 파일 설정(보안이나 쓸모 없는 파일 제외

# echo "# aio4_class" >> README.md
# git init
# git add README.md
# git commit -m "first commit"
# git branch -M main
# git remote add origin https://github.com/mj-git-memory/aio4_class.git
# git push -u origin main

# git remote remove origin ????
# git pull origin main 
# git clone 주소 


# 1.로컬 pc의 작업 폴더 설정
# 2.git 원격 repository 설정
# 3.config를 통해 username / user email 정보 입력
# 4.git init 
# 5.branch를 main으로 변경
# 6.repository 연결
# 7.코드 커밋
# 8.푸시 

import random
nums = [random.randint(1, 100) for i in range(10)]
print(nums)