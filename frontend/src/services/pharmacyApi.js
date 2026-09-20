import axiosInstance from "../axiosInstance";

export const getPharmacies = () => {
  return axiosInstance.get("/pharmacies/");
};