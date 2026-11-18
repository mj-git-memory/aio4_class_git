from main import mask_bad_words


def test_mask_bad_words():
    # 각 항목은 (설명, 원본 메시지, 금지어 목록, 예상 결과) 순서이다.
    cases = [
        ("한국어", "너는 바보야", ["바보"], "너는 **야"),
        ("대소문자 무시", "BAD Bad bad bAd", ["bad"], "*** *** *** ***"),
        ("금지어 목록의 대문자", "bad", ["BAD"], "***"),
        ("여러 금지어", "바보! BAD 말고 게임해요.", ["바보", "bad"], "**! *** 말고 게임해요."),
        ("반복 및 연속 등장", "바보바보 바보", ["바보"], "**** **"),
        ("금지어 없음", "Hello, 즐거운 게임!", ["바보"], "Hello, 즐거운 게임!"),
        ("빈 메시지", "", ["bad"], ""),
        ("빈 금지어 목록", "Hello!", [], "Hello!"),
        ("빈 금지어 무시", "BAD!", ["", "bad"], "***!"),
        ("중복 금지어", "bad", ["bad", "BAD", "bad"], "***"),
        ("특수문자 그대로 검색", "a.b a+b axb", ["a.b", "a+b"], "*** *** axb"),
        ("공백 줄바꿈 이모지 보존", "Hi!  BAD\n바보🙂", ["bad", "바보"], "Hi!  ***\n**🙂"),
        ("단어 내부도 검색", "badminton", ["bad"], "***minton"),
        ("같은 금지어의 겹침", "ababa", ["aba"], "*****"),
        ("다른 금지어의 겹침", "abcde", ["abc", "cde"], "*****"),
        ("금지어 순서 반대", "abcde", ["cde", "abc"], "*****"),
        ("한 글자 금지어", "Aa!", ["a"], "**!"),
        ("메시지보다 긴 금지어", "hi", ["hello"], "hi"),
    ]

    for description, message, bad_words, expected in cases:
        original_words = bad_words.copy()
        actual = mask_bad_words(message, bad_words)
        # 결과, 반환 타입, 길이 보존, 입력 목록 보존을 확인한다.
        assert actual == expected, f"{description}: {actual!r} != {expected!r}"
        assert isinstance(actual, str)
        assert len(actual) == len(message)
        assert bad_words == original_words
        print(f"통과: {description}")

    print(f"전체 {len(cases)}개 테스트 통과")


if __name__ == "__main__":
    test_mask_bad_words()
