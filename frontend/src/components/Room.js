import React, { useState, useEffect } from "react";
import { Grid, Button, Typography, responsiveFontSizes} from "@mui/material";
import { useParams, useNavigate } from "react-router-dom";
import CreateRoomPage from "./CreateRoomPage";
import MusicPlayer from "./MusicPlayer"

const Room = (props) => {
    // init state
    const [state, setState] = useState({
        votesToSkip: 0,
        guestCanPause: false,
        isHost: false,
        showSettings: false,
        spotifyAuthenticated: false,
        song: {},
    });

    const navigate = useNavigate();
    let { roomCode } = useParams();
    let interval = null;

    // will run after the component has rendered initially
    useEffect(() => {
        getRoomDetails();
        interval = setInterval(getCurSong, 1000);
        return () => {
            clearInterval(interval)
        }
    }, []);

    const getRoomDetails = async () => {
        // calling get_room in local app api
        const response = await fetch(`/api/get_room?code=${roomCode}`);
        if (!response.ok) {
            props.leaveRoomCallback();
            navigate("/");
            return;
        }

        const data = await response.json();
        setState((prevState) => ({
            ...prevState,
            votesToSkip: data.votes_to_skip,
            guestCanPause: data.guest_can_pause,
            isHost: data.is_host,
        }));
        if (data.is_host) {
            authenticateSpotify();
        }
    };

    const authenticateSpotify = async () => {
        // calling is_authenticated from local app spotify
        const response = await fetch("/spotify/is_authenticated");
        const data = await response.json();
        setState((prevState) => ({
            ...prevState,
            spotifyAuthenticated: data.status,
        }));
        if (!data.status) {
            // calling geth_auth_url from local app spotify
            const authUrlResponse = await fetch("/spotify/get_auth_url");
            const authUrlData = await authUrlResponse.json();
            window.location.replace(authUrlData.url)
        }
    };

    const getCurSong = async () => {
        // calling cur_song from local app spotify
        const response = await fetch("/spotify/cur_song");
        if (!response.ok) {
            console.log('Response is not ok ' + response)
            return;
        }
        const data = await response.json();
        setState((prevState) => ({
            ...prevState,
            song: data,
        }));
    };

    const leaveButtonPressed = async () => {
        const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            };
        await fetch("/api/leave_room", requestOptions);
        props.leaveRoomCallback();
        navigate("/");
    };

    const updateShowSettings = (value) => {
        // updating state
        setState(prevState => ({
            ...prevState, showSettings: value
        }));
    };

    const renderSettings = () => (
        <Grid container spacing={1}>
          <Grid item xs={12} align="center">
            <CreateRoomPage
                update={true}
                votesToSkip={state.votesToSkip}
                guestCanPause={state.guestCanPause}
                roomCode={roomCode}
                updateCallback={getRoomDetails}
            />
          </Grid>
          <Grid item xs={12} align="center">
            <Button variant="contained" color="secondary" onClick={() => updateShowSettings(false)}>Close</Button>
          </Grid>
        </Grid>
    );

    const renderSettingsButton = () => (
        <Grid item xs={12} align="center">
          <Button variant="contained" color="primary" onClick={() => updateShowSettings(true)}>Settings</Button>
        </Grid>
    );

    if (state.showSettings) {
        return renderSettings();
    }

    return (
        <Grid container spacing={1}>
        <Grid item xs={12} align="center">
            <Typography variant="h4" component="h4">
              Code: {roomCode}
            </Typography>
          </Grid>
          <MusicPlayer
            time={state.song.time}
            duration={state.song.duration}
            image_url={state.song.image_url}
            title={state.song.title}
            artist={state.song.artist}
            is_playing={state.song.is_playing}
          />
          <Grid item xs={12} align="center">
            <Typography variant="h6" component="h6">
              Votes : {state.song.votes} / {state.song.votes_required}
            </Typography>
          </Grid>
          <Grid item xs={12} align="center">
            <Typography variant="h6" component="h6">
              Guest Can Pause: {state.guestCanPause.toString()}
            </Typography>
          </Grid>
          <Grid item xs={12} align="center">
            <Typography variant="h6" component="h6">
              Host: {state.isHost.toString()}
            </Typography>
          </Grid>
          {state.isHost ? renderSettingsButton() : null}
          <Grid item xs={12} align="center">
            <Button variant="contained" color="secondary" onClick={leaveButtonPressed}>Leave Room</Button>
          </Grid>
        </Grid>
    );
}

export default Room;
