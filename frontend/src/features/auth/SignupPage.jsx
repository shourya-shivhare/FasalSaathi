import React from 'react';
import { LoginPage } from './LoginPage';

export const SignupPage = () => {
  // Since FasalSaathi uses passwordless phone number + OTP, 
  // registration and login are unified in a single flow.
  return <LoginPage />;
};
