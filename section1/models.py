from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ValidationError
from datetime import datetime
from django.db import models

# Create your models here.


class Quarter(models.Model):
    report_quarter = models.CharField(max_length=6, unique=True)  # e.g., "2024Q1", "2024Q2"
    start_date = models.DateField()
    end_date = models.DateField()

    def get_absolute_url(self):
        return reverse("quarter_detail", args=[str(self.id)])
    
    def __str__(self):
        return self.report_quarter

class Month(models.Model):
    report_month = models.CharField(max_length=6, unique=True)  # e.g., "202401", "202402"
    quarter = models.ForeignKey(Quarter, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.report_month
    class Meta:
        unique_together = ('quarter', 'report_month')

class Family(models.Model):
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    case_number = models.CharField(max_length=11)
    county_fips_code = models.CharField(max_length=3)
    stratum = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=5)
    FUNDING_STREAMS = (
        ("1", "TANF Federal Funds"),
        ("2", "State Only Funds"),
    )
    funding_stream = models.CharField(max_length=1, choices=FUNDING_STREAMS)
    DISPOSITIONS = (("1", "Data Collection Complete"),)
    disposition = models.CharField(max_length=1, choices=DISPOSITIONS)
    APPLICANT = (("1", "New Applicant" ),
                 ("2", "No"),)
    new_applicant = models.CharField(max_length=1, choices=APPLICANT)
    num_family_members = models.CharField(max_length=2)
    FAMILY_TYPES = (("1", "Single Parent"),
                    ("2", "Two Parent"),
                    ("3", "Child Only"),)
    family_type = models.CharField(max_length=1, choices=FAMILY_TYPES)
    HOUSING = (("1", "Public Housing"),
               ("2", "Rent Subsidy"),
               ("3", "No Subsidy"),)
    receives_subsidized_housing = models.CharField(max_length=1, choices=HOUSING)
    MEDICAL = (("1", "Yes, Medicid/CHIP"),
               ("2", "No"),)
    receives_medical_assistance = models.CharField(max_length=1, choices=MEDICAL)
    receives_snap = models.CharField(max_length=1, default='0')
    snap_amount = models.CharField(max_length=4)
    receives_subsidized_child_care = models.CharField(max_length=1, default='0')
    subsid_child_care_amount = models.CharField(max_length=4)
    child_support_amount = models.CharField(max_length=4)
    family_cash_resources = models.CharField(max_length=4)
    #cash_and_equivalents
    item21a_amount = models.CharField(max_length=4)
    item21b_nbr_month = models.CharField(max_length=3)
    #tanf_child_care
    item22a_amount = models.CharField(max_length=4)
    item22b_children_covered = models.CharField(max_length=2)
    item22c_nbr_months = models.CharField(max_length=3)
    item23a_amount = models.CharField(max_length=4)
    item23b_nbr_months = models.CharField(max_length=3)
    item24a_amount = models.CharField(max_length=4, default='0000')
    item24b_amount = models.CharField(max_length=3, default='000')
    item25a_amount = models.CharField(max_length=4, default='0000')
    item25b_amount = models.CharField(max_length=3, default='000')
    item26a1_sanc_redux_amt = models.CharField(max_length=4)
    ITEM26 = (("1", "Yes"),
               ("2", "No"),)
    item26a2_work_req_sanction = models.CharField(max_length=1, choices=ITEM26)
    item26a4_teen_prnt_schl_attend_sanc = models.CharField(max_length=1, choices=ITEM26)
    item26a5_child_support_non_coop = models.CharField(max_length=1, choices=ITEM26)
    item26a6_irp_non_coop = models.CharField(max_length=1, choices=ITEM26)
    item26a7_other_sanction = models.CharField(max_length=1, choices=ITEM26)
    item26b_recoupment = models.CharField(max_length=4)
    item26c1_other_tot_red_amount = models.CharField(max_length=4)
    item26c2_family_cap = models.CharField(max_length=1, choices=ITEM26)
    item26c3_red_len_assist = models.CharField(max_length=1, choices=ITEM26)
    item26c4_other_non_sanction = models.CharField(max_length=1, choices=ITEM26)
    waiver_eval_gprs = models.CharField(max_length=1, default='0')
    FED_TL_EXEMPT = (("01", "Not Federal Exempt"),
                     ("02", "Exempt-No ActiveHOH/Spouse"),
                     ("03", "Exempt-StateOnlyFunds"),
                     ("04", "Exempt-Lvng Indian/Alaska Country"),
                     ("05", "No longer in Use"))
    fam_exempt_fed_time_limits = models.CharField(max_length=2, choices=FED_TL_EXEMPT)
    new_child_only = models.CharField(max_length=1, default='0')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                   on_delete=models.CASCADE,
                                   related_name='created_family',
                                   null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                   on_delete=models.CASCADE,
                                   related_name='updated_family',
                                   null=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('month', 'case_number')

    def get_absolute_url(self):
        return reverse('family-detail', kwargs={'pk':self.pk})

    def save(self, *args, **kwargs):
        fields_to_check = ['case_number', 'county_fips_code', 'stratum', 'zip_code', 'funding_stream', \
                'disposition', 'new_applicant', 'num_family_members', 'family_type', \
                'receives_subsidized_housing', 'receives_medical_assistance', 'snap_amount', \
                'subsid_child_care_amount', 'child_support_amount', 'family_cash_resources',\
                'item21a_amount', 'item21b_nbr_month', 'item22a_amount', 'item22b_children_covered', \
                'item22c_nbr_months', 'item23a_amount', 'item23b_nbr_months', 'item26a1_sanc_redux_amt', \
                'item26a2_work_req_sanction', 'item26a4_teen_prnt_schl_attend_sanc', \
                'item26a5_child_support_non_coop', 'item26a6_irp_non_coop', 'item26a7_other_sanction',\
                'item26b_recoupment', 'item26c1_other_tot_red_amount', 'item26c2_family_cap',\
                'item26c3_red_len_assist', 'item26c4_other_non_sanction', 'fam_exempt_fed_time_limits'
                ]
        
        for field_name in fields_to_check:
            field_value = getattr(self, field_name)
            field = self._meta.get_field(field_name)  # Get the field object
            max_length = field.max_length  # Read the max_length of the field

            if self._is_valid_integer(field_value):
                # If valid, format with leading zeros based on the field's max_length
                formatted_value = field_value.zfill(max_length)
                setattr(self, field_name, formatted_value)
            else:
                # If the value is not a valid integer, raise an error
                raise ValueError(f"The value of {field_name} must be an integer and fit within its length  of {max_length}.")

        super().save(*args, **kwargs)  # Call the "real" save() method.

    def _is_valid_integer(self, value):
        try:
            # Convert to integer
            int_value = int(value)
            return True
        except ValueError:
            # If conversion to integer fails, it's not a valid integer
            return False

        
class Adult(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    AFFILIATIONS = (
        ("1", "Receiving TANF Assistance"),
        ("2", "Parent of Minor receiving assistane"),
        ("3", "Caretaker relative of Minor receiving assistane"),
        ("5", "Person's income/resource counted, not receiving assistance"),
    )
    family_affiliation= models.CharField(max_length=1, choices= AFFILIATIONS)
    NCP = (
        ("1", "Yes, a Non-Custodial Parent"),
        ("2", "No"),
    )
    noncustodial_parent= models.CharField(max_length=1, choices=NCP)
    date_of_birth= models.CharField(max_length=8)
    ssn= models.CharField(max_length=9)
    YESNO = (
        ("1", "Yes"),
        ("2", "No"),
    )
    item34a_hispanic_latino= models.CharField(max_length=1, choices=YESNO)
    item34b_american_indian_alaska_native= models.CharField(max_length=1, choices=YESNO)
    item34c_asian= models.CharField(max_length=1, choices=YESNO)
    item34d_black= models.CharField(max_length=1, choices=YESNO)
    item34e_native_pacific_islander = models.CharField(max_length=1, choices=YESNO)
    item34f_white= models.CharField(max_length=1, choices=YESNO)
    GENDERS = (
        ("1", "Male"),
        ("2", "Female"),
        ("3", "Non-binary"),
        ("4", "Uses a different term"),
        ("5", "Unknown/Refused to say"),
    )
    gender= models.CharField(max_length=1, choices=GENDERS)
    item36a_receives_oasdi = models.CharField(max_length=1, choices=YESNO)
    item36b_receives_federal_disability = models.CharField(max_length=1, choices=YESNO)
    item36c_receives_title_xiv_apdt= models.CharField(max_length=1, choices=YESNO)
    item36d = models.CharField(max_length=1, default='0')
    item36e_receives_xvi_ssi= models.CharField(max_length=1, choices=YESNO)
    MARITALSTATUS = (
        ("1", "Single, Never Married"),
        ("2", "Married"),
        ("4", "Widowed"),
        ("5", "Divorced"),
    )
    marital_status= models.CharField(max_length=1, choices=MARITALSTATUS)
    HOH = (
        ("01", "Head-of-Household"),
        ("02", "Spouse of HoH"),
        ("03", "Other (Parent, child, sibling..)"),
        ("04", "Unrelated Adult"),
    )
    relationship_to_hoh = models.CharField(max_length=2, choices=HOH)
    MINORPRNT = (
        ("1", "Yes, ParentWithMinor and is 2 Parent"),
        ("2", "Yes, ParentWithMinor and not 2 Parent"),
        ("3", "No, Not a ParentWithMinor"),
    )
    parent_with_minor_child= models.CharField(max_length=1, choices=MINORPRNT)
    pregnant_woman_needs=models.CharField(max_length=1,default='0')
    EDULEVELS = (
        ("01", "Grade 1"),
        ("02", "Grade 2"),
        ("03", "Grade 3"),
        ("04", "Grade 4"),
        ("05", "Grade 5"),
        ("06", "Grade 6"),
        ("07", "Grade 7"),
        ("08", "Grade 8"),
        ("09", "Grade 9"),
        ("10", "Grade 10"),
        ("11", "Grade 11"),
        ("12", "HSD/GED/12th"),
        ("13", "Associate's Degree"),
        ("14", "Bachelor's Degree"),
        ("15", "Graduate Degree"),
        ("16", "Other Credentials"),
        ("98", "No Formal Education"),
        ("99", "Unknown"),
    )
    educational_level= models.CharField(max_length=2, choices=EDULEVELS)
    NATIONALITY = (
        ("1", "U.S Citizen"),
        ("2", "Qualified Alien"),
        ("9", "Unknown"),
    )
    citizenship_immigration_status= models.CharField(max_length=1, choices=NATIONALITY)
    YESNONA = (
        ("1", "Yes, has cooperated with Child Support"),
        ("2", "No"),
        ("9", "Not Applicable"),
    )
    coop_child_support= models.CharField(max_length=1, choices=YESNONA)
    countable_federal_time_limit_months = models.CharField(max_length=3)
    remaining_state_limit = models.CharField(max_length=2, default='00')
    exempt_from_state_limit = models.CharField(max_length=1, default='0')
    EMPSTS = (
        ("1", "Employed"),
        ("2", "UnEmployed, Looking for Work"),
        ("3", "UnEmployed, Not Looking for Work"),
    )
    employment_status= models.CharField(max_length=1, choices=EMPSTS)
    WEI = (
        ("01", "Yes, Adult WEI receiving Assistance",),
        ("02", "Yes, Sanctioned Non-recipient WEI Parent"),
        ("03", "Yes, Non-recipeint-TimeLimit  WEI Parent"),
        ("04", "Yes, Non-recipient WEI SSI Parent"),
        ("05", "Yes, Non-recipient WEI Parent Other reason"),
        ("06", "No WEI, Non-recipient Non-Parent/Other"),
        ("07", "No WEI due to Immigration Status"),
        ("08", "No, Non-recipient WEI SSI Parent"),
        ("09", "No WEI Parent caring for a disabled member"),
        ("11", "No WEI MinorParent not HoH"),
        ("12", "No WEI deceased individual"),
    )
    work_eligible_individual = models.CharField(max_length=2, choices=WEI)
    WPS = (
        ("99", "Not Applicable, not WEI"),
        ("01", "Disregard 1P with Child < 12"),
        ("02", "Disregard Required to Participate but not and sanctions <=3 months"),
        ("05", "Disregard based on Tribal Work Program"),
        ("07", "Disabled, excluded from 2P"),
        ("09", "Exempt, Domestic Violence Waiver"),
        ("15", "Deemed engaged-TeenParent with satisfactory school attendance"),
        ("16", "Deemed engaged-TeenParent with 20 hours of edu_related_to_employment"),
        ("17", "Deemed engaged Parent/relative with >=20 CORE hours/week + < 6 year child"),
        ("18", "Required to Participate, no other options apply"),
    )
    work_participation_status= models.CharField(max_length=2, choices=WPS)
    unsubsidized_employment_hours= models.CharField(max_length=2)
    subsidized_private_employment_hours= models.CharField(max_length=2)
    subsidized_public_employment_hours= models.CharField(max_length=2)
    #work_experience_hours = models.CharField(max_length=2)
    item53a_wex_participation= models.CharField(max_length=2)
    item53b_wex_excused_absences= models.CharField(max_length=2)
    item53c_wex_holidays= models.CharField(max_length=2)
    on_job_training_hours= models.CharField(max_length=2)
    #job_search_readiness_hours = models.CharField(max_length=2)
    item55a_jobsearch_participation= models.CharField(max_length=2)
    item55b_jobsearch_excused_absences= models.CharField(max_length=2)
    item55c_jobsearch_holidays= models.CharField(max_length=2)
    #community_svs_prog_hours = models.CharField(max_length=2)
    item56a_commsvs_participation= models.CharField(max_length=2)
    item56b_commsvs_excused_absences= models.CharField(max_length=2)
    item56c_commsvs_holidays= models.CharField(max_length=2)
    #vocational_education_hours = models.CharField(max_length=2)
    item57a_voced_participation= models.CharField(max_length=2)
    item57b_voced_excused_absences= models.CharField(max_length=2)
    item57c_voced_holidays= models.CharField(max_length=2)
    #job_skills_training_hours = models.CharField(max_length=2)
    item58a_jst_participation= models.CharField(max_length=2)
    item58b_jst_excused_absences= models.CharField(max_length=2)
    item58c_jst_holidays= models.CharField(max_length=2)
    #ed_related_to_employmentno_hsd_hours = models.CharField(max_length=2)
    item59a_emped_hsd_participation= models.CharField(max_length=2)
    item59b_emped_hsd_excused_absences= models.CharField(max_length=2)
    item59c_emped_hsd_holidays= models.CharField(max_length=2)
    #satisfactory_school_attendence_hours = models.CharField(max_length=2)
    item60a_schlattnd_participation= models.CharField(max_length=2) #goes to 59a, b and c
    item60b_schlattnd_excused_absences= models.CharField(max_length=2) #goes to 59a, b and c
    item60c_schlattnd_holidays= models.CharField(max_length=2) #goes to 59a, b and c
    #providing_child_care_hours = models.CharField(max_length=2)
    item61a_chldcare_participation= models.CharField(max_length=2) #goes to 59a, b and c
    item61b_chldcare_excused_absences= models.CharField(max_length=2) #goes to 59a, b and c
    item61c_chldcare_holidays= models.CharField(max_length=2) #goes to 59a, b and c
    other_work_activities= models.CharField(max_length=2)
    deemed_core_hours_overall_rate= models.CharField(max_length=2)
    deemed_core_hours_two_parent_rate= models.CharField(max_length=2)
    earned_income = models.CharField(max_length=4)
    item66a_earned_income_tax_credit= models.CharField(max_length=4, default='0000')
    item66b_social_security= models.CharField(max_length=4)
    item66c_ssi= models.CharField(max_length=4)
    item66d_worker_comp = models.CharField(max_length=4)
    item66e_other_unearned_income= models.CharField(max_length=4)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                   on_delete=models.CASCADE,
                                   related_name='created_adult',
                                   null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                   on_delete=models.CASCADE,
                                   related_name='updated_adult',
                                   null=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('family', 'ssn')

    def get_absolute_url(self):
        return reverse('adult-detail', kwargs={'pk':self.pk})
        
class Child(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    AFFILIATIONS = (
        ("1", "Receiving TANF Assistance"),
        ("2", "Parent of Minor receiving assistane"),
        ("3", "Caretaker relative of Minor receiving assistane"),
        ("2", "Person's income/resource counted, not receiving assistance"),
    )
    family_affiliation= models.CharField(max_length=1, choices= AFFILIATIONS)
    date_of_birth= models.CharField(max_length=8)
    ssn= models.CharField(max_length=9)
    YESNO = (
        ("1", "Yes"),
        ("2", "No"),
    )
    item34a_hispanic_latino= models.CharField(max_length=1, choices=YESNO)
    item34b_american_indian_alaska_native= models.CharField(max_length=1, choices=YESNO)
    item34c_asian= models.CharField(max_length=1, choices=YESNO)
    item34d_black= models.CharField(max_length=1, choices=YESNO)
    item34e_native_pacific_islander = models.CharField(max_length=1, choices=YESNO)
    item34f_white= models.CharField(max_length=1, choices=YESNO)
    GENDERS = (
        ("1", "Male"),
        ("2", "Female"),
        ("3", "Non-binary"),
        ("4", "Uses a different term"),
        ("5", "Unknown/Refused to say"),
    )
    gender= models.CharField(max_length=1, choices=GENDERS)
    disability_non_ssa = models.CharField(max_length=1, choices=YESNO)
    item72b_ssi_xvi_ssi = models.CharField(max_length=1, choices=YESNO)
    HOH = (
        ("04", "Child"),
        ("05", "StepChild"),
        ("06", "Great/GrandChild"),
        ("07", "Other Relative"),
        ("08", "Foster Child"),
        ("09", "Unrelated Child"),
    )
    relation_to_hoh = models.CharField(max_length=2, choices=HOH)
    MINORS = (
        ("2", "Yes, Non HOH/Souse Parent with Minor Child"),
        ("3", "No, Not a Parent with Minor Child"),
    )
    parent_with_minor_child = models.CharField(max_length=1, choices=MINORS)

    EDULEVELS = (
        ("01", "Grade 1"),
        ("02", "Grade 2"),
        ("03", "Grade 3"),
        ("04", "Grade 4"),
        ("05", "Grade 5"),
        ("06", "Grade 6"),
        ("07", "Grade 7"),
        ("08", "Grade 8"),
        ("09", "Grade 9"),
        ("10", "Grade 10"),
        ("11", "Grade 11"),
        ("12", "HSD/GED/12th"),
        ("13", "Associate's Degree"),
        ("14", "Bachelor's Degree"),
        ("15", "Graduate Degree"),
        ("16", "Other Credentials"),
        ("98", "No Formal Education"),
        ("99", "Unknown"),
    )
    educational_level= models.CharField(max_length=2, choices=EDULEVELS)
    NATIONALITY = (
        ("1", "U.S Citizen"),
        ("2", "Qualified Alien"),
        ("9", "Unknown"),
    )
    citizenship_immigration_status= models.CharField(max_length=1, choices=NATIONALITY)
    item77a_ssa = models.CharField(max_length=4)
    item77b_other_unearned_income = models.CharField(max_length=4)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                   on_delete=models.CASCADE,
                                   related_name='created_child',
                                   null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                   on_delete=models.CASCADE,
                                   related_name='updated_child',
                                   null=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('family', 'ssn')

    def get_absolute_url(self):
        return reverse('child_detail', kwargs={'pk':self.pk})

class ValidationResult(models.Model):
    report_month = models.CharField(max_length=6)  # Format: YYYYMM
    version = models.IntegerField(default=0)
    #case_number = models.CharField(max_length=11)
    #case_number_ssn = models.CharField(max_length=11)
    ERRORTYPES = (
        ("1", "WARNING"),
        ("2", "FATAL"),
        ("3", "NOERROR"),
    )
    edit_type = models.CharField(max_length=1, choices=ERRORTYPES)
    edit_number = models.CharField(max_length=6)
    item_number = models.CharField(max_length=2)
    description = models.CharField(max_length=200)
    edit_values = models.CharField(max_length=200)
    #error_flag = models.TextField()
    #error_description = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                   on_delete=models.CASCADE,
                                   related_name='created_validator',
                                   null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                   on_delete=models.CASCADE,
                                   related_name='updated_validator',
                                   null=False)
    updated_at = models.DateTimeField(auto_now=True)

    adult = models.ForeignKey(Adult, on_delete=models.CASCADE, null=True, blank=True, related_name='validation_results')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True, related_name='validation_results')

    '''
    class Meta:
        unique_together = ('report_month', 'version', 'case_number', 'edit_number', )
    '''
    
class FileUpload(models.Model):
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    MODEL_CHOICES = [
        ('family', 'Family'),
        ('adult', 'Adult'),
        ('child', 'Child'),
    ]
    model_type = models.CharField(max_length=10, choices=MODEL_CHOICES)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                   on_delete=models.CASCADE,
                                   related_name='updated_fileuploader',
                                   null=False)
    uploaded_at = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')

    def __str__(self):
        return f"{self.model_type} file for {self.month} uploaded on {self.uploaded_at}"

    @property
    def file_url(self):
        if self.file and hasattr(self.file, 'url'):
            return self.file.url
        return None

class ImportError(models.Model):
    upload = models.ForeignKey(FileUpload, on_delete=models.CASCADE)
    model_type = models.CharField(max_length=10)
    error = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                   on_delete=models.CASCADE,
                                   related_name='import_creator',
                                   null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                   on_delete=models.CASCADE,
                                   related_name='import_updater',
                                   null=False)
    updated_at = models.DateTimeField(auto_now=True)

class GeneratedFile(models.Model):
    quarter = models.ForeignKey(Quarter, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='generated_files/%Y/%m/%d/')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                   on_delete=models.CASCADE,
                                   related_name='file_creator',
                                   null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def file_url(self):
        if self.file and hasattr(self.file, 'url'):
            return self.file.url
        return None