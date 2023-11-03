import React, {useState} from "react";
import { TextField, Button, Grid, Typography } from "@mui/material";
import { Link, useNavigate } from "react-router-dom";

function RoomJoinPage() {
    // init state var as empty
    const [roomCode, setRoomCode] = useState("");
    // init state error false
    const [error, setError] = useState(false);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    // function for TextField
    const handleTextFieldChange = (e) => {
        // fetches the value and updates the roomCode of state
        setRoomCode(e.target.value);
    };

    // function for create a room btn
    const roomButtonPressed = async () => {
        // async updates the state to Loading till full code operation is complete
        setLoading(true);

        const requestOptions = {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                code: roomCode,
            })
        };

        try {
            const response = await fetch("/api/join_room", requestOptions);

            if (response.ok) {
                navigate(`/room/${roomCode}`)
                console.log("Joined room successfully");
            } else {
                setError(true);
            }
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
   };

    return (
        <Grid container spacing={1}>
            <Grid item xs={12} align="center">
                <Typography variant="h4" component="h4">
                    Join a Room
                </Typography>
            </Grid>
            <Grid item xs={12} align="center">
                <TextField
                    error={error}
                    label="Code"
                    placeholder="Enter a Room Code"
                    value={roomCode}
                    helperText={error ? "Room not found" : ""}
                    variant="outlined"
                    onChange={handleTextFieldChange}
                />
            </Grid>
            <Grid item xs={12} align="center">
                <Button variant="contained" color="primary" onClick={roomButtonPressed}>Enter Room</Button>
            </Grid>
            <Grid item xs={12} align="center">
                <Button variant="contained" color="secondary" to="/" component={Link}>Back</Button>
            </Grid>
        </Grid>
    );
}

export default RoomJoinPage;