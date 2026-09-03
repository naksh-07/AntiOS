package calc

import "testing"

func TestMultiply(t *testing.T) {
	if Multiply(2, 3) != 6 {
		t.Errorf("expected 6")
	}
}
