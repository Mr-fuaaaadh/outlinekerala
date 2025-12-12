from django.contrib import admin
from .models import Ward, ElectionResult


# --------------------------
# Inline candidates inside Ward
# --------------------------
class CandidateInline(admin.TabularInline):
    model = ElectionResult
    extra = 1
    fields = ("name", "party", "vote_count", "age", "candidate_photo", "party_logo")
    show_change_link = True


# --------------------------
# Ward Admin
# --------------------------
@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ("ward_number", "ward_name", "total_voters")
    search_fields = ("ward_number", "ward_name")
    inlines = [CandidateInline]


# --------------------------
# ElectionResult Admin
# --------------------------
@admin.register(ElectionResult)
class ElectionResultAdmin(admin.ModelAdmin):
    list_display = ("name", "party", "ward", "vote_count")
    list_filter = ("ward", "party")
    search_fields = ("name", "party", "ward__ward_name")
    autocomplete_fields = ("ward",)
