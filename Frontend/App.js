import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import { SignUp } from "./pages/signUp/SignUp.jsx";
import { Login } from "./pages/login/Login.jsx";
import { UserProvider } from "./context/userContext/userContextProvider.js";
import ProtectedRoute from "./common-components/ProtectedRoute/ProtectedRoute.jsx";
import Layout from "./common-components/pageLayout/Layout.jsx";
import NotAuthorized from "./common-components/NotAuthorized/NotAuthorized.jsx";
import { Home } from "./pages/Home/Home.jsx";
import "./global.css";
import { History } from "pages/History/History.jsx";
import { Profile } from "pages/Profile/Profile.jsx";
import { ErrorProvider } from "context/errorContext/errorContextProvider";
import { ErrorDialog } from "common-components/ErrorDialog/ErrorDialog.jsx";
import Requests from "pages/Requests/Requests.jsx"
import ResetPassword from "pages/reset_password/resetPassword.jsx";
function App() {
    return (
        <ErrorProvider>
        <ErrorDialog/>
        <UserProvider>
            <div className="App">
                <Router>
                    <Routes>
                        <Route path="/login" element={<Login />} />
                        <Route path="/signUp" element={<SignUp />} />
                        <Route path="*" element={<div>404 Not Found</div>} />
                        <Route exact path="/notAuthorized" element={<NotAuthorized />} />
                        <Route exact path="/reset_password" element={<ResetPassword/>}/>

                        {/* Protected routes */}
                        <Route element={<Layout />}>
                            <Route element={<ProtectedRoute/>}>
                                <Route exact path="/" element={<Home />} />
                            </Route>
                            <Route path="/history" element={<ProtectedRoute  requiredRole={"rider"}/>}>
                                <Route path="/history" element={<History/>} />
                            </Route>
                            <Route path="/requests" element={<ProtectedRoute  requiredRole={"admin"}/>}>
                                <Route path="/requests" element={<Requests/>} />
                            </Route>
                            <Route  element={<ProtectedRoute/>}>
                                <Route path="/profile" element={<Profile/>} />
                            </Route>
                        </Route>
                    </Routes>
                </Router>
            </div>
        </UserProvider>
        </ErrorProvider>
    );
}

export default App;
