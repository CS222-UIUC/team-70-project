import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Avatar from '@sabfry/avatarium';
import { Formik, Form, Field } from 'formik';
import './ProfilePage.css';
export function ProfilePage() {
    
    const [profile, setProfile] = useState(null);
    useEffect(() => {
        axios.get('http://localhost:3000/profile')
            .then((response) => {
                setProfile(response.data);
            }).catch((error) => {
                console.error('Error:', error);
                setProfile({
                    name: 'Demo User',
                    email: 'demo@example.com'
                });
            });
    }, []);
    console.log(profile);
    if (!profile) {
        return (
            <div className="profile-page">
                <h1>Loading Profile...</h1>
            </div>
        );
    }
    return (
        <div className="profile-page">
            <h1>Profile Page</h1>
            <div className="profile-info">
                {/* <Avatar theme="blobs" /> */}
                <h2>{profile.name}</h2>
                <p>{profile.email}</p>
                {/* <Formik
                    initialValues={{ name: profile.name, email: profile.email }}
                    onSubmit={(values, { setSubmitting }) => {
                        axios.post('http://localhost:3000/profile/update', values)
                            .then(response => {
                                setProfile(response.data);
                                setSubmitting(false);
                            })
                            .catch(error => {
                                console.error('Error updating user data:', error);
                                setSubmitting(false);
                            });
                    }}
                >
                    <p>{({ isSubmitting }) => (
                        <Form>
                            <div>
                                <label htmlFor="name">Name</label>
                                <Field id="name" name="name" placeholder="John Doe" />
                            </div>
                            <div>
                                <label htmlFor="email">Email</label>
                                <Field id="email" name="email" placeholder="john.doe@example.com" type="email" />
                            </div>
                            <button type="submit" disabled={isSubmitting}>
                                Update
                            </button>
                        </Form>
                    )}</p> 
                </Formik> */}
            </div>
        </div>
    );
}
