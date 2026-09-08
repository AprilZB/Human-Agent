export const mockAphrLogin = async (employeeId: string) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        token: 'mock_token_' + employeeId,
        user: { employeeId, role: 'TEAM_LEADER', name: 'Mock User' }
      })
    }, 500)
  })
}
