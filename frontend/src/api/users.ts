import api from './index'

export interface User {
  id: number
  username: string
  role: string
  created_at: string
}

export interface CreateUserPayload {
  username: string
  password: string
  role: 'admin' | 'viewer'
}

export const getUsers = async (): Promise<User[]> => {
  const response = await api.get<User[]>('/users')
  return response.data
}

export const createUser = async (payload: CreateUserPayload): Promise<User> => {
  const response = await api.post<User>('/users', payload)
  return response.data
}

export const deleteUser = async (id: number): Promise<void> => {
  await api.delete(`/users/${id}`)
}
