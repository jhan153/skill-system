//go:build windows

package workcontract

import (
	"errors"
	"os"
	"syscall"
	"unsafe"
)

const lockFileExclusive = 0x00000002

var (
	kernel32UnlockFile = syscall.NewLazyDLL("kernel32.dll").NewProc("UnlockFileEx")
	kernel32LockFile   = syscall.NewLazyDLL("kernel32.dll").NewProc("LockFileEx")
)

func lockFile(file *os.File) error {
	var overlapped syscall.Overlapped
	result, _, callErr := kernel32LockFile.Call(
		file.Fd(),
		lockFileExclusive,
		0,
		1,
		0,
		uintptr(unsafe.Pointer(&overlapped)),
	)
	if result != 0 {
		return nil
	}
	if !errors.Is(callErr, syscall.Errno(0)) {
		return callErr
	}
	return syscall.EINVAL
}

func unlockFile(file *os.File) error {
	var overlapped syscall.Overlapped
	result, _, callErr := kernel32UnlockFile.Call(
		file.Fd(),
		0,
		1,
		0,
		uintptr(unsafe.Pointer(&overlapped)),
	)
	if result != 0 {
		return nil
	}
	if !errors.Is(callErr, syscall.Errno(0)) {
		return callErr
	}
	return syscall.EINVAL
}
