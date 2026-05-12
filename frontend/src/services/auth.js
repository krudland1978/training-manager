const USER_POOL_ID = import.meta.env.VITE_COGNITO_USER_POOL_ID
const CLIENT_ID = import.meta.env.VITE_COGNITO_CLIENT_ID
const TOKEN_KEY = 'tm_id_token'

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  sessionStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  sessionStorage.removeItem(TOKEN_KEY)
}

export function isAuthenticated() {
  return Boolean(getToken())
}

export async function login(email, password) {
  const endpoint = `https://cognito-idp.${import.meta.env.VITE_AWS_REGION}.amazonaws.com/`
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-amz-json-1.1',
      'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth',
    },
    body: JSON.stringify({
      AuthFlow: 'USER_PASSWORD_AUTH',
      ClientId: CLIENT_ID,
      AuthParameters: { USERNAME: email, PASSWORD: password },
    }),
  })
  if (!response.ok) {
    const err = await response.json()
    throw new Error(err.message || 'Login failed')
  }
  const data = await response.json()
  const token = data.AuthenticationResult?.IdToken
  if (!token) throw new Error('No token in response')
  setToken(token)
  return token
}

export function logout() {
  clearToken()
}
