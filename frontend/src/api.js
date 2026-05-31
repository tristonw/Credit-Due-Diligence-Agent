import axios from "axios";

const api = axios.create({ baseURL: "/api" });

export const listEmployees = () => api.get("/employees").then((r) => r.data);
export const getEmployee = (id) => api.get(`/employees/${id}`).then((r) => r.data);
export const createEmployee = (description, name) =>
  api.post("/employees", { description, name }).then((r) => r.data);

export const uploadCorpus = (id, payload) =>
  api.post(`/employees/${id}/corpus`, payload).then((r) => r.data);
export const listCorpus = (id) => api.get(`/employees/${id}/corpus`).then((r) => r.data);
export const updateCorpus = (id, corpusId, patch) =>
  api.patch(`/employees/${id}/corpus/${corpusId}`, patch).then((r) => r.data);
export const train = (id) => api.post(`/employees/${id}/train`).then((r) => r.data);

export const judge = (id, transcript, ground_truth = null) =>
  api.post(`/employees/${id}/judge`, { transcript, ground_truth }).then((r) => r.data);
export const evaluateJudgment = (id) =>
  api.post(`/employees/${id}/evaluate-judgment`).then((r) => r.data);
export const listJudgments = (id) =>
  api.get(`/employees/${id}/judgments`).then((r) => r.data);

export const evaluate = (id, phase) =>
  api.post(`/employees/${id}/evaluate`, { phase }).then((r) => r.data);
export const compareEval = (id) =>
  api.get(`/employees/${id}/evaluations/compare`).then((r) => r.data);

export const getDeposits = (id) => api.get(`/employees/${id}/deposits`).then((r) => r.data);
export const getLeveling = (id) => api.get(`/employees/${id}/leveling`).then((r) => r.data);
export const getExperienceLog = (id) =>
  api.get(`/employees/${id}/experience-log`).then((r) => r.data);
export const getLevelingCurve = (maxLevel = 10) =>
  api.get("/leveling-curve", { params: { max_level: maxLevel } }).then((r) => r.data);
export const getStats = () => api.get("/stats").then((r) => r.data);

export const runTask = (id, prompt) =>
  api.post(`/employees/${id}/tasks`, { prompt }).then((r) => r.data);
export const labelTask = (taskId, rating) =>
  api.post(`/tasks/${taskId}/label`, { rating }).then((r) => r.data);

export const listPromotions = (status = "pending") =>
  api.get("/promotions", { params: { status } }).then((r) => r.data);
export const decidePromotion = (id, approve, expert) =>
  api.post(`/promotions/${id}/decide`, { approve, expert }).then((r) => r.data);
