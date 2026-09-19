from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import mark_safe

from .models import (
    Users,
    UserProfile,
    RegistrationRequest,
)


# ============================================================
# USERS ADMIN
# ============================================================

@admin.register(Users)
class CustomUserAdmin(UserAdmin):

    ordering = ["email"]

    list_display = (
        "email",
        "username",
        "role",
        "is_superuser",
        "is_staff",
        "is_active",
        "date_joined",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    search_fields = (
        "email",
        "username",
    )

    readonly_fields = (
        "date_joined",
        "last_login",
    )

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "email",
                    "username",
                    "password",
                )
            },
        ),

        (
            "Role",
            {
                "fields": (
                    "role",
                )
            },
        ),

        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),

        (
            "Security",
            {
                "fields": (
                    "token_version",
                    "last_logout",
                )
            },
        ),

        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),

                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


# ============================================================
# REGISTRATION REQUEST ADMIN
# ============================================================

@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):

    # --------------------------------------------------------
    # List page
    # --------------------------------------------------------

    list_display = (
        "id",
        "email",
        "username",
        "role",
        "status",
        "created_at",
        "reviewed_by",
        "reviewed_at",
    )

    list_filter = (
        "role",
        "status",
        "created_at",
        "reviewed_at",
    )

    search_fields = (
        "email",
        "username",
        "citizenship_number",
        "pharmacy_license_number",
    )

    ordering = (
        "-created_at",
    )

    # --------------------------------------------------------
    # Read-only fields
    # --------------------------------------------------------

    readonly_fields = (
        "created_at",
        "updated_at",
        "reviewed_at",
        "reviewed_by",
        "citizenship_front_preview",
        "citizenship_back_preview",
        "pharmacy_license_preview",
    )

    # --------------------------------------------------------
    # Admin form
    # --------------------------------------------------------

    fieldsets = (

        (
            "Registration Information",
            {
                "fields": (
                    "email",
                    "username",
                    "role",
                    "phone_number",
                    "password",
                )
            },
        ),

        (
            "Patient Verification",
            {
                "fields": (
                    "citizenship_number",
                    "citizenship_front",
                    "citizenship_front_preview",
                    "citizenship_back",
                    "citizenship_back_preview",
                ),

                "description": (
                    "Patient citizenship documents."
                ),
            },
        ),

        (
            "Pharmacy Verification",
            {
                "fields": (
                    "pharmacy_license_number",
                    "pharmacy_license_document",
                    "pharmacy_license_preview",
                ),

                "description": (
                    "Pharmacy licence information."
                ),
            },
        ),

        (
            "Verification",
            {
                "fields": (
                    "status",
                    "rejection_reason",
                    "reviewed_by",
                    "reviewed_at",
                )
            },
        ),

        (
            "Dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    # ========================================================
    # CITIZENSHIP FRONT PREVIEW
    # ========================================================

    def citizenship_front_preview(
        self,
        obj
    ):

        if (
            obj.citizenship_front
            and hasattr(
                obj.citizenship_front,
                "url"
            )
        ):

            return mark_safe(
                f'''
                <div>
                    <img
                        src="{obj.citizenship_front.url}"
                        style="
                            max-width: 600px;
                            max-height: 400px;
                            object-fit: contain;
                            border: 1px solid #ddd;
                            border-radius: 8px;
                            padding: 5px;
                            background: #fff;
                        "
                    />
                </div>
                '''
            )

        return "No citizenship front image."

    citizenship_front_preview.short_description = (
        "Citizenship Front Preview"
    )

    # ========================================================
    # CITIZENSHIP BACK PREVIEW
    # ========================================================

    def citizenship_back_preview(
        self,
        obj
    ):

        if (
            obj.citizenship_back
            and hasattr(
                obj.citizenship_back,
                "url"
            )
        ):

            return mark_safe(
                f'''
                <div>
                    <img
                        src="{obj.citizenship_back.url}"
                        style="
                            max-width: 600px;
                            max-height: 400px;
                            object-fit: contain;
                            border: 1px solid #ddd;
                            border-radius: 8px;
                            padding: 5px;
                            background: #fff;
                        "
                    />
                </div>
                '''
            )

        return "No citizenship back image."

    citizenship_back_preview.short_description = (
        "Citizenship Back Preview"
    )

    # ========================================================
    # PHARMACY LICENCE PREVIEW
    # ========================================================

    def pharmacy_license_preview(
        self,
        obj
    ):

        if (
            obj.pharmacy_license_document
            and hasattr(
                obj.pharmacy_license_document,
                "url"
            )
        ):

            url = obj.pharmacy_license_document.url

            # Image preview
            if url.lower().endswith(
                (
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".webp",
                )
            ):

                return mark_safe(
                    f'''
                    <div>
                        <img
                            src="{url}"
                            style="
                                max-width: 600px;
                                max-height: 400px;
                                object-fit: contain;
                                border: 1px solid #ddd;
                                border-radius: 8px;
                                padding: 5px;
                                background: #fff;
                            "
                        />
                    </div>
                    '''
                )

            # PDF / other document
            return mark_safe(
                f'''
                <a
                    href="{url}"
                    target="_blank"
                    style="
                        display: inline-block;
                        padding: 10px 15px;
                        background: #417690;
                        color: white;
                        border-radius: 5px;
                        text-decoration: none;
                    "
                >
                    Open Pharmacy Licence Document
                </a>
                '''
            )

        return "No pharmacy licence document."

    pharmacy_license_preview.short_description = (
        "Pharmacy Licence Preview"
    )

    # ========================================================
    # ACTION: ACCEPT
    # ========================================================

    actions = [
        "accept_selected",
        "deny_selected",
    ]

    @admin.action(
        description="Accept selected registrations"
    )
    def accept_selected(
        self,
        request,
        queryset
    ):

        accepted = 0
        skipped = 0

        for registration in queryset:

            if registration.status != "pending":

                skipped += 1
                continue

            # ----------------------------------------------
            # Check duplicate email
            # ----------------------------------------------

            if Users.objects.filter(
                email=registration.email
            ).exists():

                self.message_user(
                    request,
                    (
                        f"Skipped {registration.email}: "
                        "email already exists."
                    ),
                    level="error"
                )

                skipped += 1
                continue

            # ----------------------------------------------
            # Check duplicate username
            # ----------------------------------------------

            if Users.objects.filter(
                username=registration.username
            ).exists():

                self.message_user(
                    request,
                    (
                        f"Skipped {registration.username}: "
                        "username already exists."
                    ),
                    level="error"
                )

                skipped += 1
                continue

            # ----------------------------------------------
            # Create actual user
            # ----------------------------------------------

            user = Users(
                email=registration.email,
                username=registration.username,
                role=registration.role,
                password=registration.password,
                is_active=True,
            )

            user.save()

            # ----------------------------------------------
            # Create profile
            # ----------------------------------------------

            UserProfile.objects.create(
                user=user,
                phone_number=registration.phone_number,
            )

            # ----------------------------------------------
            # Update registration
            # ----------------------------------------------

            registration.status = "accepted"

            registration.reviewed_by = (
                request.user
            )

            registration.reviewed_at = (
                registration.updated_at
            )

            registration.rejection_reason = None

            registration.save()

            accepted += 1

        self.message_user(
            request,
            (
                f"{accepted} registration(s) accepted. "
                f"{skipped} skipped."
            )
        )

    # ========================================================
    # ACTION: DENY
    # ========================================================

    @admin.action(
        description="Deny selected registrations"
    )
    def deny_selected(
        self,
        request,
        queryset
    ):

        denied = 0
        skipped = 0

        for registration in queryset:

            if registration.status != "pending":

                skipped += 1
                continue

            registration.status = "denied"

            registration.reviewed_by = (
                request.user
            )

            registration.reviewed_at = (
                timezone.now()
            )

            registration.rejection_reason = (
                "Registration denied by administrator."
            )

            registration.save()

            denied += 1

        self.message_user(
            request,
            (
                f"{denied} registration(s) denied. "
                f"{skipped} skipped."
            )
        )


# ============================================================
# USER PROFILE ADMIN
# ============================================================

@admin.register(UserProfile)
class UserProfileAdmin(
    admin.ModelAdmin
):

    list_display = (
        "user",
        "profile_image_tag",
        "phone_number",
        "location",
        "birth_date",
        "created_at",
    )

    readonly_fields = (
        "profile_image_tag",
    )

    search_fields = (
        "user__email",
        "user__username",
        "phone_number",
    )

    list_filter = (
        "location",
        "birth_date",
    )

    def profile_image_tag(
        self,
        obj
    ):

        if (
            obj.profile_image
            and hasattr(
                obj.profile_image,
                "url"
            )
        ):

            return mark_safe(
                f'''
                <img
                    src="{obj.profile_image.url}"
                    width="80"
                    height="80"
                    style="
                        object-fit: cover;
                        border-radius: 5px;
                    "
                />
                '''
            )

        return "Image not available"

    profile_image_tag.short_description = (
        "Profile Image"
    )
