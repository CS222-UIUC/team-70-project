import React from 'react';
import styled from 'styled-components';
import './App.css';
import Keyboard from './Components/keyboard';

function App() {
  
  return (
    <Container>
      <LeftSidebar>
        <SidebarTitle>Previous Guesses/Scores</SidebarTitle>
      </LeftSidebar>

      <MainContent>
        <Header>
          <Title>Wikipedle</Title>
        </Header>
        
        <ContentArea>
        <TextContainerWrapper>
          </TextContainerWrapper>

          
          <NavBar>
            <NavItems>
              <NavItemBold>Article</NavItemBold>
              <NavItemLink>Talk</NavItemLink>
              <NavSpacer />
              <NavItemBold>Read</NavItemBold>
              <NavItemLink>View source</NavItemLink>
              <NavItemLink>View History</NavItemLink>
              <NavItemLink>Tools</NavItemLink>
            </NavItems>
            <NavLine />
            <ActiveNavIndicators>
              <ActiveIndicator style={{ left: '0', width: '40px' }} />
              <ActiveIndicator style={{ right: '340px', width: '29px' }} />
            </ActiveNavIndicators>
            <NavLine />
          </NavBar>
          
          <ContentColumns>
            <MainArticle>
              <ScrambledText>Scrambled Introductory Blurb Text</ScrambledText>
            </MainArticle>
            
            <SideArticle>
              <BlurredImageContainer>
                <BlurredImageText>Blurred Image</BlurredImageText>
              </BlurredImageContainer>
            </SideArticle>
          </ContentColumns>
        </ContentArea>
        
        <Footer>
          <KeyboardWrapper>
            <Keyboard/>
          </KeyboardWrapper>
          
        </Footer>
      </MainContent>
      
      <RightSidebar>
        <SidebarTitle>Friend Scores Leaderboard</SidebarTitle>
      </RightSidebar>
    </Container>
  );
}

// Styled Components
const Container = styled.div`
  display: flex;
  width: 100%;
  max-width: 1280px;
  min-height: 100vh;
  margin: 0 auto;
  background: #FFFFFF;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;
const TextContainerWrapper = styled.div`
  width: 100%;
  min-height: 50px;
  border: 1px solid rgba(0,0,0,0.25);
  overflow: auto;
  border-radius: 4px;
  margin-bottom: 20px;
  
  pre {
    text-align: left;
    display: block;
    width: calc(100% - 40px);
    margin: 0;
    padding: 20px;
    font-size: 20px;
  }
`;

const LeftSidebar = styled.div`
  width: 200px;
  background: #D9D9D9;
  padding: 20px 10px;
  
  @media (max-width: 1024px) {
    width: 180px;
  }
  
  @media (max-width: 768px) {
    width: 100%;
    order: 2;
  }
`;

const RightSidebar = styled.div`
  width: 200px;
  background: #D9D9D9;
  padding: 20px 10px;
  
  @media (max-width: 1024px) {
    width: 180px;
  }
  
  @media (max-width: 768px) {
    width: 100%;
    order: 3;
  }
`;

const SidebarTitle = styled.h3`
  font-family: 'Archivo', sans-serif;
  font-weight: 400;
  font-size: 16px;
  color: #000000;
  margin-top: 200px;
  
  @media (max-width: 768px) {
    margin-top: 20px;
    text-align: center;
  }
`;

const MainContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; // Fixes flexbox overflow issues
`;

const Header = styled.div`
  width: 100%;
  padding: 10px 20px;
  background: #E8FFBE;
  display: flex;
  align-items: center;
  justify-content: center;
  
  @media (min-width: 769px) {
    justify-content: flex-start;
  }
`;

const Title = styled.h1`
  font-family: 'Gideon Roman', serif;
  font-weight: 400;
  font-size: 40px;
  color: #000000;
  
  @media (min-width: 769px) {
    margin-left: 40px;
  }
  
  @media (max-width: 480px) {
    font-size: 32px;
  }
`;

const ContentArea = styled.div`
  flex: 1;
  padding: 20px;
  overflow-x: hidden;
`;



const NavBar = styled.div`
  position: relative;
  margin-bottom: 40px;
`;

const NavItems = styled.div`
  display: flex;
  padding: 10px 0;
  overflow-x: auto;
  
  @media (max-width: 600px) {
    justify-content: space-between;
  }
`;

const NavItemBold = styled.span`
  font-family: 'Archivo', sans-serif;
  font-weight: 700;
  font-size: 12px;
  color: #000000;
  margin-right: 15px;
  white-space: nowrap;
`;

const NavItemLink = styled.span`
  font-family: 'Archivo', sans-serif;
  font-weight: 400;
  font-size: 12px;
  color: #0059FF;
  margin-right: 15px;
  white-space: nowrap;
  cursor: pointer;
`;

const NavSpacer = styled.div`
  flex: 1;
  min-width: 20px;
`;

const NavLine = styled.div`
  width: 100%;
  height: 1px;
  background: #5A5A5A;
  margin: 5px 0;
`;

const ActiveNavIndicators = styled.div`
  position: relative;
  height: 2px;
  width: 100%;
`;

const ActiveIndicator = styled.div`
  position: absolute;
  height: 2px;
  background: #000000;
  bottom: 0;
`;

const ContentColumns = styled.div`
  display: flex;
  gap: 20px;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const MainArticle = styled.div`
  flex: 2;
  min-height: 300px;
  background: #D9D9D9;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
`;

const ScrambledText = styled.div`
  font-family: 'Archivo', sans-serif;
  font-weight: 400;
  font-size: 20px;
  color: #000000;
  text-align: center;
  
  @media (max-width: 480px) {
    font-size: 16px;
  }
`;

const SideArticle = styled.div`
  flex: 1;
  min-height: 300px;
  background: #D9D9D9;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
`;

const BlurredImageContainer = styled.div`
  width: 100%;
  max-width: 197px;
  aspect-ratio: 197 / 258;
  background: #F5FF62;
  display: flex;
  justify-content: center;
  align-items: center;
`;

const BlurredImageText = styled.div`
  font-family: 'Archivo', sans-serif;
  font-weight: 400;
  font-size: 20px;
  color: #000000;
  text-align: center;
  
  @media (max-width: 480px) {
    font-size: 16px;
  }
`;
const KeyboardWrapper = styled.div`
  width: 100%;
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;

  .keyboard {
    height: auto;
    width: 100%;
    max-width: 1000px;
  }

  .textcontainer {
    width: 100%;
    margin-bottom: 15px;
  }

  .keyboardcontainer {
    width: 100%;
  }

  .container {
    width: 100%;
  }
`;
const Footer = styled.div`
  width: 100%;
  padding: 20px;
  background: #E8FFBE;
  display: flex;
  justify-content: center;
  align-items: center;
`;


export default App;