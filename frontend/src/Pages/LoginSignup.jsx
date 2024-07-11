// import React, { useState } from 'react'
// import './CSS/LoginSignup.css'


// const LoginSignup = () => {

// const [state,setState] = useState("Login");
// const [formData, setFormData] = useState({
//   username:"",
//   password:"",
//   email:""
// })

// const changeHandler = (e) =>{
//   setFormData({...formData,[e.target.name]:e.target.value})

// }

// const login = async () =>{
//   console.log("Login function executed",formData);
//   let responseData;
//   console.log("hii");
//   await fetch('http://localhost:4000/login',{
//     method:'POST',
//     headers:{
//       'Accept':'application/form-data',
//       'Content-Type':'application/json',
//     },
//     body:JSON.stringify(formData),
//   }).then((resp)=>resp.json()).then((data)=>responseData=data)
//   console.log(responseData)

//   if(responseData.success){
//     localStorage.setItem('auth-token',responseData.token);
//     window.location.replace("/");
//   }
//   else{
//     alert(responseData.errors)
//   }

// }

// const signup = async () =>{
//   console.log("signup function executed",formData);
//   let responseData;
//   console.log("hii");
//   await fetch('http://localhost:4000/signup',{
//     method:'POST',
//     headers:{
//       'Accept':'application/form-data',
//       'Content-Type':'application/json',
//     },
//     body:JSON.stringify(formData),
//   }).then((resp)=>resp.json()).then((data)=>responseData=data)
//   console.log(responseData)

//   if(responseData.success){
//     localStorage.setItem('auth-token',responseData.token);
//     window.location.replace("/");
//   }
//   else{
//     alert(responseData.errors)
//   }
// }

//   return (
//     <div className='loginsignup'>
//       <div className="loginsignup-container">
//        <h1>{state}</h1>
//        <div className="loginsignup-fields">
//         {state==="Sign Up"?<input name='username' value={formData.username} onChange={changeHandler} type="text" placeholder='Your Name' />:<></>}
//         <input name='email'  value={formData.email} onChange={changeHandler} type='email' placeholder='Email Address'/>
//         <input name='password'  value={formData.password} onChange={changeHandler}type='password' placeholder='Password'/>
//        </div>
//        <button onClick={()=>{state==="Login"?login():signup()}}>Continue</button>
//        {state==="Sign Up"?<p className='loginsignup-login'>Already have  an account?<span onClick={()=>{setState("Login")}}>&nbsp;login here</span></p>:
//        <p className='loginsignup-login'>Create an account?<span onClick={()=>{setState("Sign Up")}}>&nbsp;Click here</span></p>}
       
       
//        <div className="loginsignup-agree">
//         <input type="checkbox" name='' id='' />
//         <p>By continuing, i agree to the terms of use and privacy policy.</p>
//        </div>
//       </div>
//     </div>
//   )
// }

// export default LoginSignup;


import React, { useState } from 'react';
import './CSS/LoginSignup.css';

const LoginSignup = () => {
  const [state, setState] = useState("Login");
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    email: ""
  });

  const changeHandler = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // const login = async () => {
  //   console.log("Login function executed", formData);
  //   let responseData;
  //   await fetch('http://localhost:4000/login', {
  //     method: 'POST',
  //     headers: {
  //       'Accept': 'application/form-data',
  //       'Content-Type': 'application/json',
  //     },
  //     body: JSON.stringify(formData),
  //   }).then((resp) => resp.json()).then((data) => responseData = data);
  //   console.log("response data is ",responseData);

  //   if (responseData.success) {
  //     // onLogin(responseData.token);
  //     window.location.replace("/home");

  //   } else {
  //     alert(responseData.errors);
  //   }
  // };

  // Login function in LoginSignup.jsx
const login = async () => {
  try {
    const response = await fetch('http://localhost:4000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });

    const data = await response.json();
    if (data.success) {
      localStorage.setItem('auth-token', data.token); // Store the token
      window.location.replace("/home"); // Redirect upon successful login
    } else {
      alert(data.errors);
    }
  } catch (error) {
    console.error('Login error:', error);
  }
};

  const signup = async () => {
    console.log("Signup function executed", formData);
    let response =  await fetch('http://localhost:4000/signup', {
      method: 'POST',
      headers: {
        'Accept': 'application/form-data',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });

    const data = await response.json();
    if (data.success) {
      localStorage.setItem('auth-token', data.token); // Store the token
      window.location.replace("/home"); // Redirect upon successful login
    } else {
      alert(data.errors);
    }
  };

  return (
    <div className='loginsignup'>
      <div className="loginsignup-container">
        <h1>{state}</h1>
        <div className="loginsignup-fields">
          {state === "Sign Up" ? <input name='username' value={formData.username} onChange={changeHandler} type="text" placeholder='Your Name' /> : <></>}
          <input name='email' value={formData.email} onChange={changeHandler} type='email' placeholder='Email Address' />
          <input name='password' value={formData.password} onChange={changeHandler} type='password' placeholder='Password' />
        </div>
        <button onClick={() => { state === "Login" ? login() : signup() }}>Continue</button>
        {state === "Sign Up" ? <p className='loginsignup-login'>Already have an account?<span onClick={() => { setState("Login") }}>&nbsp;Login here</span></p> :
          <p className='loginsignup-login'>Create an account?<span onClick={() => { setState("Sign Up") }}>&nbsp;Click here</span></p>}
        <div className="loginsignup-agree">
          <input type="checkbox" name='' id='' />
          <p>By continuing, I agree to the terms of use and privacy policy.</p>
        </div>
      </div>
    </div>
  );
}

export default LoginSignup;
