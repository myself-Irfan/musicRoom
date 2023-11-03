import React, { useState, useEffect } from 'react';
import RoomJoinPage from './RoomJoinPage';
import CreateRoomPage from './CreateRoomPage';
import Info from './Info';
import Room from './Room';
import { Grid, Button, ButtonGroup, Typography } from '@mui/material';
import { BrowserRouter, Route, Routes, Link, Navigate } from "react-router-dom";

//function that defines routing structure, renders different component for different URL
function HomePage() {
    // setting init state as null
    const [roomCode, setRoomCode] = useState(null);

    // this runs the fetchUserInRoom after the component is done rendering
    useEffect(() => {
        // async function waits for await block
        async function fetchUserInRoom() {
            const response = await fetch("/api/user_in_room");
            // conv response to json and store to var
            const data = await response.json();
            // set roomCode with the value associated with code param in data
            setRoomCode(data.code);
        }
        fetchUserInRoom();
    }, []);

    const renderHomePage = () => {
        return (
            <Grid container spacing={3}>
                <Grid item xs={12} align="center">
                    <Typography variant="h3" compact="h3">House Party</Typography>
                </Grid>
                <Grid item xs={12} align="center">
                    <ButtonGroup disableElevation variant="contained" color="primary">
                        <Button color="primary" to="/join" component={Link}>Join a Room</Button>
                        <Button color="info" to="/info" component={Link}>Info</Button>
                        <Button color="secondary" to="/create" component={Link}>Create a Room</Button>
                    </ButtonGroup>
                </Grid>
            </Grid>
        );
    }

    // this function is passed to Room component as a property
    const clearRoomCode = () => {
        // set roomCode as null
        setRoomCode(null);
    }

    return (
        <Routes>
            <Route path="/" element={roomCode ? <Navigate to={`/room/${roomCode}`} /> : renderHomePage()} />
            <Route path="/join" element={<RoomJoinPage />} />
            <Route path="/info" element={<Info />} />
            <Route path="/create" element={<CreateRoomPage />} />
            <Route path="/room/:roomCode" element={<Room leaveRoomCallback={clearRoomCode} />} />
        </Routes>
    );
}

//export component to be used in other component
export default HomePage;