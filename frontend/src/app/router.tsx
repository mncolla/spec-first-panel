import { Route, Switch } from 'wouter'
import { DepartmentCreatePage } from '../features/departments/components/department-create-page.tsx'
import { DepartmentDetailPage } from '../features/departments/components/department-detail-page.tsx'
import { DepartmentListPage } from '../features/departments/components/department-list-page.tsx'

export function AppRouter() {
  return (
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
  )
}
