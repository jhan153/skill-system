package workcontract

import (
	"errors"
	"os"
	"path/filepath"
	"strings"
)

type sessionLock struct {
	file      *os.File
	statePath string
}

func acquireSessionLock(sessionID string) (*sessionLock, error) {
	stateFile := statePath(sessionID)
	if stateFile == "" {
		return nil, errors.New("work-contract state root unavailable")
	}
	if err := os.MkdirAll(filepath.Dir(stateFile), 0o700); err != nil {
		return nil, err
	}
	lockFilePath := strings.TrimSuffix(stateFile, filepath.Ext(stateFile)) + ".lock"
	file, err := os.OpenFile(lockFilePath, os.O_CREATE|os.O_RDWR, 0o600)
	if err != nil {
		return nil, err
	}
	if err := file.Chmod(0o600); err != nil {
		file.Close()
		return nil, err
	}
	if err := lockFile(file); err != nil {
		file.Close()
		return nil, err
	}
	return &sessionLock{file: file, statePath: stateFile}, nil
}

func (lock *sessionLock) release() {
	if lock == nil || lock.file == nil {
		return
	}
	_ = unlockFile(lock.file)
	_ = lock.file.Close()
}

func (lock *sessionLock) owns(sessionID string) bool {
	return lock != nil && lock.file != nil && lock.statePath == statePath(sessionID)
}
