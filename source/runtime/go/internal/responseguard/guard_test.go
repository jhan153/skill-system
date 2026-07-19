package responseguard

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestCorrectionAndRecoveryContract(t *testing.T) {
	cases := []string{
		"아니 확인하지 말고 이것도 실수로 기록해",
		"이런 기본적인 실수를 왜 하는 거야",
		"내 코덱스 구성을 망가뜨렸잖아",
		"이 메시지도 수습형 답변이야",
		"That is not what I asked.",
	}
	for _, value := range cases {
		if !IsCorrection(value) {
			t.Errorf("missed correction %q", value)
		}
	}
	if IsCorrection("플랜에 반영해") {
		t.Fatal("ordinary instruction classified as correction")
	}
	for _, value := range []string{
		"실수 목록을 문서로 정리해줘",
		"실수로 파일을 삭제하지 않게 테스트를 추가해",
		"현재 코드는 잘못된 입력을 거부한다",
		"이 함수는 왜 만든 건지 설명해",
	} {
		if IsCorrection(value) {
			t.Errorf("ordinary use of correction vocabulary was classified as correction: %q", value)
		}
	}
	if !IsRecoveryOnly("맞습니다. 제가 잘못 판단했습니다. 지금부터 다시 확인하겠습니다.") {
		t.Fatal("recovery-only response was not detected")
	}
	if IsRecoveryOnly("맞습니다. 원인은 설명 요청을 작업 명령으로 바꿨기 때문입니다. 앞으로 구분하겠습니다.") {
		t.Fatal("direct explanation was blocked")
	}
	if IsRecoveryOnly("맞습니다. Stop 출력 계약을 decision block으로 수정했습니다. 앞으로 공식 계약을 확인하겠습니다.") {
		t.Fatal("completed concrete action was blocked")
	}
	for _, value := range []string{
		"맞습니다. ```go\nfunc fixed() {}\n``` 지금부터 다시 확인하겠습니다.",
		"맞습니다. [수정 파일](/Users/example/repo/fix.go) 앞으로 제대로 하겠습니다.",
		"맞습니다. 현재 상태입니다. 지금부터 다시 검토하겠습니다.",
		"맞습니다. 원인은 다음과 같습니다. 앞으로 다시 확인하겠습니다.",
	} {
		if !IsRecoveryOnly(value) {
			t.Errorf("non-substantive recovery bypassed guard: %q", value)
		}
	}
}

func TestStateContainsNoRawTextAndBlocksOnce(t *testing.T) {
	root := t.TempDir()
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", root)
	prompt := "아니 그게 아니라 요구사항을 다시 봐 raw-secret"
	correction, err := Prompt("session", "turn", prompt)
	if err != nil || !correction {
		t.Fatalf("prompt result correction=%v err=%v", correction, err)
	}
	correctionRoot := filepath.Join(root, "correction-gate")
	entries, err := os.ReadDir(correctionRoot)
	if err != nil || len(entries) != 1 {
		t.Fatalf("state entries=%d err=%v", len(entries), err)
	}
	raw, err := os.ReadFile(filepath.Join(correctionRoot, entries[0].Name()))
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(raw), prompt) || strings.Contains(string(raw), "raw-secret") {
		t.Fatal("raw prompt persisted")
	}
	blocked, err := Stop("session", "turn", "맞습니다. 지금부터 다시 검토하겠습니다.")
	if err != nil || !blocked {
		t.Fatalf("first stop blocked=%v err=%v", blocked, err)
	}
	blocked, err = Stop("session", "turn", "맞습니다. 지금부터 다시 검토하겠습니다.")
	if err != nil || blocked {
		t.Fatalf("second stop blocked=%v err=%v", blocked, err)
	}
}

func TestOrdinaryPromptDoesNotCreateState(t *testing.T) {
	root := t.TempDir()
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", root)
	correction, err := Prompt("session", "turn", "플랜에 반영해")
	if err != nil || correction {
		t.Fatalf("ordinary prompt correction=%v err=%v", correction, err)
	}
	entries, err := os.ReadDir(filepath.Join(root, "correction-gate"))
	if err != nil && !os.IsNotExist(err) {
		t.Fatal(err)
	}
	if len(entries) != 0 {
		t.Fatalf("ordinary prompt wrote %d state entries", len(entries))
	}
}
