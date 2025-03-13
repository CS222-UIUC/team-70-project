import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const NavLinkContainer = styled.div`
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 100;
`;

const StyledLink = styled(Link)`
  padding: 8px 15px;
  background-color: #E8FFBE;
  color: #000000;
  text-decoration: none;
  border-radius: 4px;
  font-family: 'Archivo', sans-serif;
  font-size: 14px;
  font-weight: bold;
  
  &:hover {
    background-color: #d4e9aa;
  }
`;

const NavLink = ({ currentPath }) => {
  return (
    <NavLinkContainer>
      {currentPath === "/profile" ? (
        <StyledLink to="/">Back to Game</StyledLink>
      ) : (
        <StyledLink to="/profile">Profile</StyledLink>
      )}
    </NavLinkContainer>
  );
};

export default NavLink;