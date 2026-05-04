from django.db import models

# Create your models here.
  
class Employee(models.Model): 
    # ── spec.2a(i): Attributes ───────────────────────────────── 
    name         = models.CharField(max_length=200) 
    id_number    = models.CharField(max_length=100, unique=True)
    rate         = models.FloatField() 
    overtime_pay = models.FloatField(null=True, blank=True)
    allowance    = models.FloatField(null=True, blank=True)
  
    # ── spec.2a(ii): Methods ─────────────────────────────────── 
    def getName(self): 
        return self.name 
  
    def getID(self): 
        return self.id_number 
  
    def getRate(self): 
        return self.rate 
  
    def getOvertime(self): 
        return self.overtime_pay 
  
    def resetOvertime(self): 
        """Spec §I.6: Resets overtime_pay to 0 after a payslip is generated.""" 
        self.overtime_pay = 0 
        self.save() 
  
    def getAllowance(self): 
        return self.allowance 
  
    def __str__(self): 
        # spec: prints "pk: id_number, rate: rate" 
        return f"pk: {self.id_number}, rate: {self.rate}"

class Payslip(models.Model): 
    # ── spec.2b(i): Attributes ───────────────────────────────── 
    # ForeignKey to Employee via id_number field (not default pk) 
    id_number          = models.ForeignKey(Employee, to_field="id_number", 
                                           on_delete=models.CASCADE, 
                                           related_name="payslips") 
    month              = models.CharField(max_length=50) 
    date_range         = models.CharField(max_length=100) 
    year               = models.CharField(max_length=10) 
    pay_cycle          = models.IntegerField() 
    rate               = models.FloatField() 
    earnings_allowance = models.FloatField() 
    deductions_tax     = models.FloatField() 
    deductions_health  = models.FloatField()  # Philhealth (Cycle 2) or 0 
    pag_ibig           = models.FloatField()  # Cycle 1 only 
    sss                = models.FloatField()  # Cycle 2 only 
    overtime           = models.FloatField() 
    total_pay          = models.FloatField() 
  
    # ── spec.2b(ii): Methods ─────────────────────────────────── 
    def getIDNumber(self):   return self.id_number.id_number 
    def getMonth(self):      return self.month 
    def getDate_range(self): return self.date_range 
    def getYear(self):       return self.year 
    def getPay_cycle(self):  return self.pay_cycle 
    def getRate(self):       return self.rate 
  
    def getCycleRate(self): 
        """Returns 1/2 of the monthly rate (per-cycle base pay).""" 
        return self.rate / 2 
    
    def get_total_deductions(self):
        gross_pay = self.getCycleRate() + self.earnings_allowance + self.overtime
        return gross_pay - self.total_pay
    
    def getEarnings_allowance(self): return self.earnings_allowance 
    def getDeductions_tax(self):     return self.deductions_tax 
    def getDeductions_health(self):  return self.deductions_health 

    def getPag_ibig(self):           return self.pag_ibig
    def getSSS(self):                return self.sss
    def getOvertime(self):           return self.overtime
    def getTotal_pay(self):          return self.total_pay

    def __str__(self):
        return (
            f"pk: {self.pk}, Employee: {self.id_number.id_number}, "
            f"Period: {self.month} {self.date_range}, {self.year}, "
            f"Cycle: {self.pay_cycle}, Total Pay: {self.total_pay}"
        )