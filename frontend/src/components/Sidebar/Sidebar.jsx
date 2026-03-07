import { NavLink } from 'react-router-dom'
import './Sidebar.css'
import homeIcon from '../../assets/icons/home.svg'
import accountIcon from '../../assets/icons/account.svg'
import notificationsIcon from '../../assets/icons/notifications.svg'

export default function Sidebar() {

    return (
        <aside className="fixed top-0 left-0 h-screen w-55 bg-brand-purple text-brand-pink shadow-right-sidebar shrink-0 flex flex-col">
            <h1 className="font-title title pl-4" style={{fontSize:'1.65rem'}}>Token Trail</h1>
            <div className="grow">
                <nav>
                    <ul>
                        <li>
                            <NavLink 
                                to="/dashboard" 
                                className={({isActive}) => 
                                    `flex items-center gap-2 ${isActive?  "bg-purple-clicked" : ""}`
                                }
                            >
                                {({isActive}) => (
                                    <>
                                        <div className={`w-2 h-10 ${isActive? "bg-[#FEF7FFBF]" : ""}`}/>
                                        <img src={homeIcon} alt="Home"/>
                                        <span>Home</span>
                                    </>
                                )}
                                
                            </NavLink>
                        </li>
                    </ul>
                </nav>
            </div>
            <div className="h-17 border-t border-t-[#FFFFFF80] flex">
                <button className='flex-1 shadow-button flex items-center justify-center'>
                    <img src={accountIcon} alt="Account"/>
                </button>
                <button className='flex-1 shadow-button flex items-center justify-center'>
                    <img src={notificationsIcon} alt="Notifications"/>
                </button>
            </div>
        </aside>
    )
}