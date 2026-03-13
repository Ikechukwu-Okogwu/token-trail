import Sidebar from "../components/Sidebar/Sidebar"

export default function CoursePage({ courses = []}) {
  return(
    <div className="h-screen flex">
      <Sidebar courses={courses}/>
      <main className="ml-55 flex-1">
      </main>
    </div>
  )
}