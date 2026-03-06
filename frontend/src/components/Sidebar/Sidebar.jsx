import { NavLink } from 'react-router-dom'
import './Sidebar.css'
import homeIcon from '../../assets/icons/home.svg'

export default function Sidebar() {

    return (
        <aside className="fixed top-0 left-0 h-screen w-55 bg-brand-purple text-brand-pink shadow-right shrink-0 flex flex-col">
            <h1 className="font-title title pl-4" style={{fontSize:'1.65rem'}}>Token Trail</h1>
            <div className="grow">
                <nav>
                    <ul>
                        <li>
                            <NavLink to="/dashboard" className="flex items-center gap-2">
                                <img src={homeIcon} alt="Home"/>
                                <span>Home</span>
                            </NavLink>
                        </li>
                    </ul>
                </nav>
            </div>
            
        </aside>
    )
}