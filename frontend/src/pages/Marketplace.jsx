import React from 'react'
import { Navigate } from 'react-router-dom'

// Marketplace feature removed — redirect users to pricing
export default function Marketplace() {
  return <Navigate to="/pricing" replace />
}



