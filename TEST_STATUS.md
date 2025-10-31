# Test Status Quick Reference 🧪

## 🚀 Easiest Ways to Check Tests

### **Option 1: One Command (Recommended)**

```bash
./check_tests.sh
```

Shows both local and GitHub test status instantly!

---

### **Option 2: Just Local Tests**

```bash
./check_tests.sh local
```

or

```bash
pytest tests/ -v
```

---

### **Option 3: Check GitHub Status**

```bash
./check_tests.sh github
```

or visit:
https://github.com/ncrypteam/ncrypt/actions

---

## 📊 Current Test Status

**Local Tests**: ✅ 17/17 passing

```
TestBB84Protocol:
  ✅ test_protocol_initialization
  ✅ test_random_bit_generation
  ✅ test_qubit_preparation
  ✅ test_key_sifting
  ✅ test_full_protocol_low_noise
  ✅ test_full_protocol_high_noise

TestQuantumEncryption:
  ✅ test_key_to_bytes
  ✅ test_encrypt_decrypt
  ✅ test_decrypt_wrong_key
  ✅ test_file_encryption

TestQuantumSimulator:
  ✅ test_simulator_initialization
  ✅ test_qubit_state_creation
  ✅ test_measurement
  ✅ test_channel_quality

TestKeyManager:
  ✅ test_save_and_load_key
  ✅ test_list_keys
  ✅ test_delete_key
```

---

## 🎯 Quick Commands

```bash
# Check everything
./check_tests.sh

# Run only failed tests (after fixing)
pytest tests/ --lf

# Run specific test
pytest tests/test_basic.py::TestBB84Protocol::test_key_sifting -v

# Watch tests (auto-rerun on file change)
pip install pytest-watch
ptw tests/

# Check GitHub Actions live
./check_tests.sh watch
```

---

## 🔧 Setup GitHub Actions (First Time Only)

```bash
# 1. Commit the workflow file
git add .github/workflows/tests.yml
git commit -m "Add GitHub Actions CI"

# 2. Push to GitHub
git push

# 3. Check it's running
./check_tests.sh github
```

That's it! Now tests run automatically on every push! 🎉

---

## 📱 Get Notifications

### Email notifications:
- Go to: https://github.com/settings/notifications
- Enable "Actions" notifications
- Get email when tests fail

### Desktop notifications (with GitHub CLI):
```bash
brew install gh
gh auth login
gh run watch  # Shows live updates
```

---

## 🎨 Test Coverage

Current coverage: **~90%**

See detailed coverage:
```bash
pytest tests/ --cov=ncrypt --cov-report=html
open htmlcov/index.html
```

---

## 🐛 If Tests Fail

### 1. See what failed:
```bash
pytest tests/ -v --tb=short
```

### 2. Run only that test:
```bash
pytest tests/test_basic.py::TestName::test_that_failed -v
```

### 3. Debug with print statements:
```bash
pytest tests/ -v -s  # -s shows print() output
```

### 4. Check GitHub logs:
```bash
gh run view --log-failed
```

---

## ✅ Before Pushing Code

**Quick pre-push checklist:**

```bash
# 1. Run tests
./check_tests.sh local

# 2. Check linting (if you have it)
flake8 ncrypt/

# 3. Commit
git add .
git commit -m "Your changes"

# 4. Push
git push

# 5. Verify on GitHub
./check_tests.sh github
```

---

## 🎓 For Fresh Grads: Why This Matters

**Without CI/CD:**
```
You: "It works on my machine! 🤷"
Teammate: "Well it doesn't work on mine 😤"
```

**With GitHub Actions:**
```
✅ Tests run on clean environment (like Ubuntu)
✅ Everyone sees the same results
✅ Can't merge broken code (if you set it up)
✅ Automatic quality checks
✅ Professional workflow
```

---

## 📚 Learn More

- **GitHub Actions Setup**: See `GITHUB_ACTIONS_SETUP.md`
- **Writing Tests**: See `tests/test_basic.py` for examples
- **Test Script Source**: See `check_tests.sh` for the CLI tool

---

**Remember**: Green badge = Happy code! 🟢✨

