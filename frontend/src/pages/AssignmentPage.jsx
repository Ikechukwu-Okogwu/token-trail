import Sidebar from "../components/Sidebar/Sidebar"

export default function AssignmentPage({ courses = [] }) {

  return(
    <div className="h-screen flex">
      <Sidebar courses={courses}></Sidebar>
      <main className="ml-55 flex-1">
        <h2>Assignment page</h2>
      </main>
    </div>
  )
}