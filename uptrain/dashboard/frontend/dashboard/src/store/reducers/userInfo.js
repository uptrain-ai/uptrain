import { createSlice } from "@reduxjs/toolkit";

const userInfoSlice = createSlice({
  name: "userInfo",
  initialState: {
    credits_total: "nill",
    credits_used: "nill",
    user_name: "open source user",
    uptrain_access_token: "default_key",
  },
  reducers: {
    addUserData(state, action) {
      const { credits_total, credits_used, user_name, api_key } =
        action.payload;
      state.credits_total = credits_total;
      state.credits_used = credits_used;
      state.user_name = user_name;
      state.uptrain_access_token = api_key;
    },
    removeUserData(state, action) {
      state.credits_total = null;
      state.credits_used = null;
      state.user_name = null;
      state.uptrain_access_token = null;
    },
  },
});

export const { addUserData } = userInfoSlice.actions;
export default userInfoSlice.reducer;
export const selectUserName = (state) => state.userInfo.user_name;
export const selectTotalCredits = (state) => state.userInfo.credits_total;
export const selectUsedCredits = (state) => state.userInfo.credits_used;
export const selectUptrainAccessKey = (state) =>
  state.userInfo.uptrain_access_token;
