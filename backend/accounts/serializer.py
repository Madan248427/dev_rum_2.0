from django.contrib.auth import (
    authenticate,
    get_user_model,
)
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings

from rest_framework import serializers

from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)

from .models import (
    Users,
    UserProfile,
    RegistrationRequest,
    PasswordResetOTP,
)


User = get_user_model()


# ============================================================
# CUSTOM USER SERIALIZER
# ============================================================

class CustomUserSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = User

        fields = [
            "id",
            "email",
            "username",
            "role",
        ]


# ============================================================
# REGISTRATION SERIALIZER
# ============================================================

class RegistrationSerializer(
    serializers.ModelSerializer
):

    password = serializers.CharField(
        write_only=True,
        min_length=6
    )

    class Meta:

        model = RegistrationRequest

        fields = [
            "email",
            "username",
            "password",
            "role",
            "phone_number",

            # Patient
            "citizenship_number",
            "citizenship_front",
            "citizenship_back",

            # Pharmacy
            "pharmacy_license_number",
            "pharmacy_license_document",
        ]

        extra_kwargs = {

            "phone_number": {
                "required": False
            },

            "citizenship_number": {
                "required": False
            },

            "citizenship_front": {
                "required": False
            },

            "citizenship_back": {
                "required": False
            },

            "pharmacy_license_number": {
                "required": False
            },

            "pharmacy_license_document": {
                "required": False
            },
        }

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate_email(self, value):

        value = value.lower()

        # Check actual users
        if Users.objects.filter(
            email=value
        ).exists():

            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        # Check pending registration
        if RegistrationRequest.objects.filter(
            email=value,
            status="pending"
        ).exists():

            raise serializers.ValidationError(
                "A registration with this email is already pending."
            )

        return value

    def validate_username(self, value):

        if Users.objects.filter(
            username=value
        ).exists():

            raise serializers.ValidationError(
                "This username is already taken."
            )

        if RegistrationRequest.objects.filter(
            username=value,
            status="pending"
        ).exists():

            raise serializers.ValidationError(
                "A registration with this username is already pending."
            )

        return value

    def validate(self, attrs):

        role = attrs.get("role")

        citizenship_number = attrs.get(
            "citizenship_number"
        )

        citizenship_front = attrs.get(
            "citizenship_front"
        )

        citizenship_back = attrs.get(
            "citizenship_back"
        )

        pharmacy_license_number = attrs.get(
            "pharmacy_license_number"
        )

        pharmacy_license_document = attrs.get(
            "pharmacy_license_document"
        )

        # ====================================================
        # PATIENT
        # ====================================================

        if role == "patient":

            if not citizenship_number:

                raise serializers.ValidationError({
                    "citizenship_number":
                    "Citizenship number is required for patients."
                })

            if not citizenship_front:

                raise serializers.ValidationError({
                    "citizenship_front":
                    "Front citizenship photo is required."
                })

            if not citizenship_back:

                raise serializers.ValidationError({
                    "citizenship_back":
                    "Back citizenship photo is required."
                })

            # Patient should not send pharmacy information
            attrs["pharmacy_license_number"] = None
            attrs["pharmacy_license_document"] = None

        # ====================================================
        # PHARMACY
        # ====================================================

        elif role == "pharmacy":

            if not pharmacy_license_number:

                raise serializers.ValidationError({
                    "pharmacy_license_number":
                    "Pharmacy licence number is required."
                })

            if not pharmacy_license_document:

                raise serializers.ValidationError({
                    "pharmacy_license_document":
                    "Pharmacy licence document is required."
                })

            # Pharmacy should not send patient information
            attrs["citizenship_number"] = None
            attrs["citizenship_front"] = None
            attrs["citizenship_back"] = None

        else:

            raise serializers.ValidationError({
                "role":
                "Role must be either patient or pharmacy."
            })

        return attrs

    # ========================================================
    # CREATE PENDING REGISTRATION
    # ========================================================

    def create(self, validated_data):

        password = validated_data.pop(
            "password"
        )

        # Hash password before storing it
        validated_data["password"] = make_password(
            password
        )

        registration = RegistrationRequest.objects.create(
            **validated_data
        )

        return registration


# ============================================================
# LOGIN SERIALIZER
# ============================================================

class LoginSerializer(
    serializers.Serializer
):

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):

        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:

            raise serializers.ValidationError(
                "Both email and password are required."
            )

        # ----------------------------------------------------
        # Check if still waiting for approval
        # ----------------------------------------------------

        pending = RegistrationRequest.objects.filter(
            email=email,
            status="pending"
        ).exists()

        if pending:

            raise serializers.ValidationError(
                "Your registration is still waiting for admin verification."
            )

        # ----------------------------------------------------
        # Check denied
        # ----------------------------------------------------

        denied = RegistrationRequest.objects.filter(
            email=email,
            status="denied"
        ).order_by("-created_at").first()

        if denied:

            # Only block if there is no accepted user
            if not Users.objects.filter(
                email=email
            ).exists():

                raise serializers.ValidationError(
                    "Your registration was denied."
                )

        # ----------------------------------------------------
        # Authenticate
        # ----------------------------------------------------

        user = authenticate(
            username=email,
            password=password
        )

        if user and user.is_active:

            return user

        raise serializers.ValidationError(
            "Incorrect email or password."
        )


# ============================================================
# USER UPDATE
# ============================================================

class UserUpdateSerializer(
    serializers.ModelSerializer
):

    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=6
    )

    current_password = serializers.CharField(
        write_only=True,
        required=False
    )

    class Meta:

        model = User

        fields = [
            "email",
            "username",
            "password",
            "current_password",
        ]

    def validate(self, attrs):

        password = attrs.get(
            "password"
        )

        current_password = attrs.get(
            "current_password"
        )

        if password and not current_password:

            raise serializers.ValidationError({
                "current_password":
                "Current password is required when changing password."
            })

        if password and current_password:

            user = self.context[
                "request"
            ].user

            if not user.check_password(
                current_password
            ):

                raise serializers.ValidationError({
                    "current_password":
                    "Current password is incorrect."
                })

        return attrs

    def update(
        self,
        instance,
        validated_data
    ):

        password = validated_data.pop(
            "password",
            None
        )

        validated_data.pop(
            "current_password",
            None
        )

        for attr, value in validated_data.items():

            setattr(
                instance,
                attr,
                value
            )

        if password:

            instance.set_password(
                password
            )

        instance.save()

        return instance


# ============================================================
# USER PROFILE
# ============================================================

class UserProfileSerializer(
    serializers.ModelSerializer
):

    email = serializers.CharField(
        source="user.email",
        read_only=True
    )

    profile_image_url = serializers.SerializerMethodField()

    class Meta:

        model = UserProfile

        fields = [
            "email",
            "bio",
            "birth_date",
            "location",
            "phone_number",
            "profile_image",
            "profile_image_url",
        ]

    def get_profile_image_url(
        self,
        obj
    ):

        request = self.context.get(
            "request"
        )

        if (
            obj.profile_image
            and hasattr(
                obj.profile_image,
                "url"
            )
        ):

            return request.build_absolute_uri(
                obj.profile_image.url
            )

        return None

    def create(
        self,
        validated_data
    ):

        user = self.context[
            "request"
        ].user

        return UserProfile.objects.create(
            user=user,
            **validated_data
        )

    def update(
        self,
        instance,
        validated_data
    ):

        for attr, value in validated_data.items():

            setattr(
                instance,
                attr,
                value
            )

        instance.save()

        return instance


# ============================================================
# USER SERIALIZER
# ============================================================

class UserSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Users

        fields = [
            "id",
            "email",
            "username",
            "role",
            "is_active",
            "date_joined",
        ]


# ============================================================
# REGISTRATION REQUEST SERIALIZER
# ============================================================

class RegistrationRequestSerializer(
    serializers.ModelSerializer
):

    reviewed_by_email = serializers.CharField(
        source="reviewed_by.email",
        read_only=True
    )

    class Meta:

        model = RegistrationRequest

        fields = [
            "id",
            "email",
            "username",
            "role",
            "phone_number",

            "citizenship_number",
            "citizenship_front",
            "citizenship_back",

            "pharmacy_license_number",
            "pharmacy_license_document",

            "status",
            "rejection_reason",

            "reviewed_by_email",
            "reviewed_at",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "status",
            "reviewed_by_email",
            "reviewed_at",
            "created_at",
            "updated_at",
        ]


# ============================================================
# REVIEW SERIALIZER
# ============================================================

class RegistrationReviewSerializer(
    serializers.Serializer
):

    status = serializers.ChoiceField(
        choices=[
            "accepted",
            "denied",
        ]
    )

    rejection_reason = serializers.CharField(
        required=False,
        allow_blank=True
    )

    def validate(self, attrs):

        if (
            attrs["status"] == "denied"
            and not attrs.get("rejection_reason")
        ):

            raise serializers.ValidationError({
                "rejection_reason":
                "A rejection reason is required when denying."
            })

        return attrs


# ============================================================
# JWT
# ============================================================

class CustomTokenObtainPairSerializer(
    TokenObtainPairSerializer
):

    @classmethod
    def get_token(
        cls,
        user
    ):

        token = super().get_token(user)

        token["token_version"] = (
            user.token_version
        )

        token["role"] = user.role

        return token


# ============================================================
# FORGOT PASSWORD
# ============================================================

class ForgotPasswordSerializer(
    serializers.Serializer
):

    email = serializers.EmailField()

    def validate_email(self, value):

        if not Users.objects.filter(
            email=value
        ).exists():

            raise serializers.ValidationError(
                "Account with this email does not exist."
            )

        return value

    def save(self):

        email = self.validated_data[
            "email"
        ]

        user = Users.objects.get(
            email=email
        )

        otp = PasswordResetOTP.generate_otp()

        PasswordResetOTP.objects.create(
            user=user,
            otp=otp
        )

        send_mail(
            subject="Your Password Reset OTP",
            message=f"Your OTP is {otp}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )


# ============================================================
# RESET PASSWORD
# ============================================================

class ResetPasswordSerializer(
    serializers.Serializer
):

    email = serializers.EmailField()

    otp = serializers.CharField(
        max_length=6
    )

    new_password = serializers.CharField(
        min_length=6
    )

    def validate(self, attrs):

        email = attrs.get(
            "email"
        )

        otp = attrs.get(
            "otp"
        )

        try:

            user = Users.objects.get(
                email=email
            )

            otp_obj = PasswordResetOTP.objects.filter(
                user=user,
                otp=otp
            ).latest(
                "created_at"
            )

        except Exception:

            raise serializers.ValidationError(
                "Invalid OTP."
            )

        attrs["user"] = user

        return attrs

    def save(self):

        user = self.validated_data[
            "user"
        ]

        password = self.validated_data[
            "new_password"
        ]

        user.set_password(
            password
        )

        user.save()

        PasswordResetOTP.objects.filter(
            user=user
        ).delete()

        