---
order: 4
exercise: 37
title: Rekening Bank
module: 7
check: strict
vars: |
  start = randint(100, 900)
  deposit = randint(50, 400)
  balance = start + deposit
expect: "{{balance}}"
---

<learn>
Method bisa mengubah state objeknya sendiri.

```python
def deposit(self, amount):
    self.balance += amount
```

`+=` menambahkan nilai ke atribut yang sudah ada.
</learn>

<instructions>
Tulis class `Account` dengan `balance` dan method `deposit(amount)`.

Sebuah akun dimulai dari **{{start}}**, lalu **{{deposit}}** disetorkan. Cetak
saldo akhirnya.
</instructions>

<help>
<hint>Simpan saldo di `self.balance`, lalu tambahkan jumlah setoran di dalam method `deposit`.</hint>
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
