import React, { useState } from "react";
// HTML elements
import Button from "@mui/material/Button";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import FormHelperText from "@mui/material/FormHelperText";
import FormControl from "@mui/material/FormControl";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
// Link is used for <a> anchor tags and useNavigate is for user interaction or state changes
import { Link, useNavigate } from "react-router-dom";
import { Collapse } from "@mui/material";
import { Alert } from "@mui/material";

export default function CreateRoomPage({
    // constructor func with default val
    update = false,
    roomCode = null,
    updateCallback = () => {},
    votesToSkip = 0,
    guestCanPause = false,
}) {

    const navigate = useNavigate();

    // init state var
    const [errorMsg, setErrorMsg] = useState("");
    const [successMsg, setSuccessMsg] = useState("");
    const [votesToSkipState, setVotesToSkipState] = useState(votesToSkip);
    const [guestCanPauseState, setGuestCanPauseState] = useState(guestCanPause);

    const handleRoomButtonPressed = () => {
        // configuring POST request to be made to the API endpoint
        const requestOptions = {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                votes_to_skip: votesToSkipState,
                guest_can_pause: guestCanPauseState,
            }),
        };
        console.log('G State: ' + guestCanPauseState);
        // makes the POST request
        fetch("/api/create_room", requestOptions)
        // conv response to json
        .then((response) => response.json())
        // nav to api with code from data of json
        .then((data) => navigate("/room/" + data.code))
    };

    const handleUpdateButtonPressed = () => {
        const requestOptions = {
            method: "PATCH",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                votes_to_skip: votesToSkipState,
                guest_can_pause: guestCanPauseState,
                code: roomCode,
            }),
        };
        fetch("/api/update_room", requestOptions).then((response) => {
            if (response.ok) {
                setSuccessMsg("Room updated successfully!");
            } else {
                setErrorMsg("Error updating room...")
            }
            updateCallback();
        });
    };

    const handleVotesChange = (e) => {
        setVotesToSkipState(e.target.value);
    };

    const handleGuestCanPauseChange = (e) => {
        setGuestCanPauseState(e.target.value);
    };

    const renderCreateButtons = () => {
        return (
            <Grid container spacing={1}>
                <Grid item xs={12} align="center">
                    <Button color="primary" variant="contained" onClick={handleRoomButtonPressed}>Create A Room</Button>
                </Grid>
                <Grid item xs={12} align="center">
                    <Button color="secondary" variant="contained" to="/" component={Link}>Back</Button>
                </Grid>
            </Grid>
        );
    };

    const renderUpdateButtons = () => {
        return (
            <Grid item xs={12} align="center">
                <Button color="primary" variant="contained" onClick={handleUpdateButtonPressed}>Update Room</Button>
            </Grid>
        );
    };

    const title = update ? "Update Room" : "Create Room";

    return (
        <Grid container spacing={1}>
            <Grid item xs={12} align="center">
                <Collapse in={errorMsg != "" || successMsg != ""}>
                    {successMsg != "" ?
                        ( <Alert severity="success" onClose={() =>{setSuccessMsg("");}}>{successMsg}</Alert>)
                        :
                        (<Alert severity="error" onClose={() =>{setErrorMsg("");}}>{errorMsg}</Alert>)}
                </Collapse>
            </Grid>
            <Grid item xs={12} align="center">
                <Typography component="h4" variant="h4">{title}</Typography>
            </Grid>
            <Grid item xs={12} align="center">
                <FormControl component="fieldset">
                    <FormHelperText><span align='center'>Guest Control of Playback State</span></FormHelperText>
                    <RadioGroup row defaultValue="false" onChange={handleGuestCanPauseChange}>
                        <FormControlLabel value="true" control={<Radio color="primary" />} label="Play/Pause" labelPlacement="bottom"/>
                        <FormControlLabel value="false" control={<Radio color="secondary" />} label="No Control" labelPlacement="bottom"/>
                    </RadioGroup>
                </FormControl>
            </Grid>
            <Grid item xs={12} align="center">
                <FormControl>
                    <TextField required type="number" onChange={handleVotesChange} defaultValue={votesToSkip} inputProps={{ min: 1, style: { textAlign: "center"}, }}/>
                    <FormHelperText><span align="center">Votes Required To Skip Song</span></FormHelperText>
                </FormControl>
            </Grid>
            { update ? renderUpdateButtons() : renderCreateButtons()}
        </Grid>
    );
}

