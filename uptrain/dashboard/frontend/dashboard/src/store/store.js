import { configureStore } from '@reduxjs/toolkit'
import userReducer from './reducers/userInfo'

export const store = configureStore({
  reducer: {
    userInfo: userReducer
  }
})