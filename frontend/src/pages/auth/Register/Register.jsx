import React, {
  useState,
} from "react";

import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  FileUp,
  UserPlus,
} from "lucide-react";

import {
  Link,
} from "react-router-dom";

import {
  registerAccount,
} from "../../../services/registrationApi";

import "./Register.css";

const Register = () => {
  const [role, setRole] =
    useState("patient");

  const [formData, setFormData] =
    useState({
      username: "",
      email: "",
      phone_number: "",
      password: "",
      confirmPassword: "",
      citizenship_number: "",
      pharmacy_license_number: "",
    });

  const [
    citizenshipFront,
    setCitizenshipFront,
  ] = useState(null);

  const [
    citizenshipBack,
    setCitizenshipBack,
  ] = useState(null);

  const [
    pharmacyLicenseDocument,
    setPharmacyLicenseDocument,
  ] = useState(null);

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState(false);

  const handleChange = (event) => {
    const {
      name,
      value,
    } = event.target;

    setFormData(
      (current) => ({
        ...current,
        [name]: value,
      })
    );
  };

  const getApiError = (err) => {
    const data =
      err.response?.data;

    if (!data) {
      return "Could not submit registration.";
    }

    if (typeof data === "string") {
      return data;
    }

    if (data.detail) {
      return data.detail;
    }

    const firstKey =
      Object.keys(data)[0];

    if (!firstKey) {
      return "Could not submit registration.";
    }

    const message =
      data[firstKey];

    if (Array.isArray(message)) {
      return message[0];
    }

    return String(message);
  };

  const handleSubmit = async (
    event
  ) => {
    event.preventDefault();

    setError("");

    if (
      !formData.username.trim() ||
      !formData.email.trim() ||
      !formData.password
    ) {
      setError(
        "Please complete all required fields."
      );

      return;
    }

    if (
      formData.password.length < 6
    ) {
      setError(
        "Password must be at least 6 characters."
      );

      return;
    }

    if (
      formData.password !==
      formData.confirmPassword
    ) {
      setError(
        "Passwords do not match."
      );

      return;
    }

    if (role === "patient") {
      if (
        !formData.citizenship_number.trim() ||
        !citizenshipFront ||
        !citizenshipBack
      ) {
        setError(
          "Citizenship number and both citizenship images are required."
        );

        return;
      }
    }

    if (role === "pharmacy") {
      if (
        !formData.pharmacy_license_number.trim() ||
        !pharmacyLicenseDocument
      ) {
        setError(
          "Pharmacy licence number and licence document are required."
        );

        return;
      }
    }

    try {
      setSubmitting(true);

      const data =
        new FormData();

      data.append(
        "username",
        formData.username.trim()
      );

      data.append(
        "email",
        formData.email.trim()
      );

      data.append(
        "password",
        formData.password
      );

      data.append(
        "role",
        role
      );

      if (
        formData.phone_number.trim()
      ) {
        data.append(
          "phone_number",
          formData.phone_number.trim()
        );
      }

      if (role === "patient") {
        data.append(
          "citizenship_number",
          formData.citizenship_number.trim()
        );

        data.append(
          "citizenship_front",
          citizenshipFront
        );

        data.append(
          "citizenship_back",
          citizenshipBack
        );
      }

      if (role === "pharmacy") {
        data.append(
          "pharmacy_license_number",
          formData.pharmacy_license_number.trim()
        );

        data.append(
          "pharmacy_license_document",
          pharmacyLicenseDocument
        );
      }

      await registerAccount(data);

      setSuccess(true);
    } catch (err) {
      console.error(
        "Registration error:",
        err
      );

      setError(
        getApiError(err)
      );
    } finally {
      setSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className="register-page">
        <div className="register-success-card">
          <CheckCircle2 size={44} />

          <h1>
            Registration Submitted
          </h1>

          <p>
            Your registration request has
            been sent for administrator
            approval.
          </p>

          <p>
            Once your account is approved,
            you can log in using the email
            and password you registered
            with.
          </p>

          <Link
            to="/login"
            className="register-login-link"
          >
            Go to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="register-page">
      <div className="register-container">
        <Link
          to="/login"
          className="register-back"
        >
          <ArrowLeft size={16} />
          Back to Login
        </Link>

        <header className="register-header">
          <span>
            NirogNepal
          </span>

          <h1>
            Create an Account
          </h1>

          <p>
            Submit your details for
            verification and account
            approval.
          </p>
        </header>

        {error && (
          <div className="register-error">
            <AlertCircle size={17} />

            <span>
              {error}
            </span>
          </div>
        )}

        <form
          className="register-form"
          onSubmit={handleSubmit}
        >
          <div className="register-role-section">
            <label>
              Register as
            </label>

            <div className="register-role-options">
              <button
                type="button"
                className={
                  role === "patient"
                    ? "active"
                    : ""
                }
                onClick={() =>
                  setRole("patient")
                }
              >
                Patient
              </button>

              <button
                type="button"
                className={
                  role === "pharmacy"
                    ? "active"
                    : ""
                }
                onClick={() =>
                  setRole("pharmacy")
                }
              >
                Pharmacy
              </button>
            </div>
          </div>

          <div className="register-grid">
            <div className="register-field">
              <label htmlFor="username">
                {role === "pharmacy"
                  ? "Pharmacy Name *"
                  : "Full Name *"}
              </label>

              <input
                id="username"
                name="username"
                type="text"
                value={
                  formData.username
                }
                onChange={
                  handleChange
                }
              />
            </div>

            <div className="register-field">
              <label htmlFor="email">
                Email *
              </label>

              <input
                id="email"
                name="email"
                type="email"
                value={
                  formData.email
                }
                onChange={
                  handleChange
                }
              />
            </div>

            <div className="register-field register-full">
              <label htmlFor="phone_number">
                Phone Number
              </label>

              <input
                id="phone_number"
                name="phone_number"
                type="text"
                value={
                  formData.phone_number
                }
                onChange={
                  handleChange
                }
              />
            </div>

            <div className="register-field">
              <label htmlFor="password">
                Password *
              </label>

              <input
                id="password"
                name="password"
                type="password"
                value={
                  formData.password
                }
                onChange={
                  handleChange
                }
                minLength={6}
              />
            </div>

            <div className="register-field">
              <label htmlFor="confirmPassword">
                Confirm Password *
              </label>

              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                value={
                  formData.confirmPassword
                }
                onChange={
                  handleChange
                }
              />
            </div>

            {role === "patient" && (
              <>
                <div className="register-field register-full">
                  <label htmlFor="citizenship_number">
                    Citizenship Number *
                  </label>

                  <input
                    id="citizenship_number"
                    name="citizenship_number"
                    type="text"
                    value={
                      formData.citizenship_number
                    }
                    onChange={
                      handleChange
                    }
                  />
                </div>

                <div className="register-field">
                  <label>
                    Citizenship Front *
                  </label>

                  <label className="register-upload">
                    <FileUp size={19} />

                    <span>
                      {citizenshipFront
                        ? citizenshipFront.name
                        : "Choose front image"}
                    </span>

                    <input
                      type="file"
                      accept="image/*"
                      onChange={(event) =>
                        setCitizenshipFront(
                          event.target
                            .files?.[0] ||
                            null
                        )
                      }
                      hidden
                    />
                  </label>
                </div>

                <div className="register-field">
                  <label>
                    Citizenship Back *
                  </label>

                  <label className="register-upload">
                    <FileUp size={19} />

                    <span>
                      {citizenshipBack
                        ? citizenshipBack.name
                        : "Choose back image"}
                    </span>

                    <input
                      type="file"
                      accept="image/*"
                      onChange={(event) =>
                        setCitizenshipBack(
                          event.target
                            .files?.[0] ||
                            null
                        )
                      }
                      hidden
                    />
                  </label>
                </div>
              </>
            )}

            {role === "pharmacy" && (
              <>
                <div className="register-field register-full">
                  <label htmlFor="pharmacy_license_number">
                    Pharmacy Licence Number *
                  </label>

                  <input
                    id="pharmacy_license_number"
                    name="pharmacy_license_number"
                    type="text"
                    value={
                      formData.pharmacy_license_number
                    }
                    onChange={
                      handleChange
                    }
                  />
                </div>

                <div className="register-field register-full">
                  <label>
                    Pharmacy Licence Document *
                  </label>

                  <label className="register-upload">
                    <FileUp size={19} />

                    <span>
                      {pharmacyLicenseDocument
                        ? pharmacyLicenseDocument.name
                        : "Choose licence document"}
                    </span>

                    <input
                      type="file"
                      accept="image/*,.pdf"
                      onChange={(event) =>
                        setPharmacyLicenseDocument(
                          event.target
                            .files?.[0] ||
                            null
                        )
                      }
                      hidden
                    />
                  </label>
                </div>
              </>
            )}
          </div>

          <button
            type="submit"
            className="register-submit"
            disabled={submitting}
          >
            <UserPlus size={17} />

            {submitting
              ? "Submitting..."
              : "Submit Registration"}
          </button>

          <p className="register-existing-account">
            Already approved?{" "}
            <Link to="/login">
              Log in
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
};

export default Register;