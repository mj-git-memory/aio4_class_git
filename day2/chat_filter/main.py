import re


def mask_bad_words(chat_message: str, bad_words: list[str]) -> str:
    """대소문자를 구분하지 않고 금지어가 포함된 모든 위치를 *로 바꾼다."""
    # 원본의 각 글자를 가릴지 기록한다. 처음에는 모두 가리지 않는다.
    should_mask = [False] * len(chat_message)

    for word in bad_words:
        # 빈 문자열은 금지어로 검색하지 않고 건너뛴다.
        if word == "":
            continue

        # escape는 .이나 + 같은 기호도 문자 그대로 검색하게 한다.
        # IGNORECASE는 대문자와 소문자를 구분하지 않도록 한다.
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        search_start = 0

        while True:
            # 이전에 정한 시작 위치부터 원본 메시지에서 금지어를 찾는다.
            match = pattern.search(chat_message, search_start)
            if match is None:
                break

            # 발견한 금지어의 모든 글자 위치를 가릴 대상으로 표시한다.
            for index in range(match.start(), match.end()):
                should_mask[index] = True

            # 한 글자 뒤부터 다시 검색해서 서로 겹치는 금지어도 찾는다.
            search_start = match.start() + 1

    result = []
    for index, character in enumerate(chat_message):
        if should_mask[index]:
            result.append("*")
        else:
            # 금지어가 아닌 글자는 대소문자, 공백, 줄바꿈까지 그대로 둔다.
            result.append(character)

    # 글자 목록을 하나의 문자열로 합쳐 반환한다.
    return "".join(result)


if __name__ == "__main__":
    print(mask_bad_words("바보! BAD 말고 즐겁게 게임해요.", ["바보", "bad"]))
