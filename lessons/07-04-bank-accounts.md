---
order: 4
exercise: 37
title: Bank Accounts
xp: 30
module: 7
vars: |
  start = randint(100, 900)
  deposit = randint(50, 400)
  balance = start + deposit
expect: "{{balance}}"
---

<learn>
Methods can change the object. That is what makes a class more than a
container of values:

```python
class Account:
    def __init__(self, balance):
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
```

`self.balance += amount` mutates the instance. After the call, the object
remembers the new value.
</learn>

<instructions>
Write a class `Account` with a `balance` and a `deposit(amount)` method.

An account starts at **{{start}}**, then **{{deposit}}** is deposited. Print
the final balance.

```python
class Account:
    def __init__(self, balance):
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

account = Account({{start}})
account.deposit({{deposit}})
print(account.balance)
```
</instructions>

<help>
<hint>Add to `self.balance` inside the method, then print `account.balance` afterwards.</hint>
<solution>
class Account:
    def __init__(self, balance):
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

account = Account({{start}})
account.deposit({{deposit}})
print(account.balance)
</solution>
</help>
