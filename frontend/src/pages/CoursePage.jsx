import Sidebar from "../components/Sidebar/Sidebar"

export default function CoursePage({ courses = [] }) {
  return(
    <div className="h-screen flex">
      <Sidebar courses={courses}></Sidebar>
      <main className="ml-55 flex-1">
        <h2>Course page</h2>
      </main>
    </div>
  )
}