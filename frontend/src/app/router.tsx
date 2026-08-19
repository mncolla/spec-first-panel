import { Route, Switch } from 'wouter'
import { LoginPage } from '../features/auth/components/login-page.tsx'
import { RequireSession } from '../features/auth/components/require-session.tsx'
import { DepartmentCreatePage } from '../features/departments/components/department-create-page.tsx'
import { DepartmentDetailPage } from '../features/departments/components/department-detail-page.tsx'
import { DepartmentListPage } from '../features/departments/components/department-list-page.tsx'
import { Shell } from './shell.tsx'

export function AppRouter() {
  return (
    <Switch>
      <Route path="/ingresar">
        <LoginPage />
      </Route>
      <Route>
        <RequireSession>
          <Shell>
            <Switch>
              <Route path="/">
                <DepartmentListPage />
              </Route>
              <Route path="/departamentos/nuevo">
                <DepartmentCreatePage />
              </Route>
              <Route path="/departamentos/:id">
                <DepartmentDetailPage />
              </Route>
            </Switch>
          </Shell>
        </RequireSession>
      </Route>
    </Switch>
  )
}
