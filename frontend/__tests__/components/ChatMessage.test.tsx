/**
 * ChatMessage Component Tests
 *
 * Example test suite for React components using React Testing Library and Jest.
 */
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock component for demonstration
// In real implementation, import your actual component:
// import ChatMessage from '@/components/ChatMessage';

// Mock ChatMessage component for this example
const ChatMessage = ({ role, content }: { role: string; content: string }) => (
  <div data-testid="chat-message" className={`message-${role}`}>
    <div className="message-role">{role}</div>
    <div className="message-content">{content}</div>
  </div>
);

describe('ChatMessage Component', () => {
  it('renders user message correctly', () => {
    render(<ChatMessage role="user" content="Hello, AI!" />);

    expect(screen.getByTestId('chat-message')).toBeInTheDocument();
    expect(screen.getByText('user')).toBeInTheDocument();
    expect(screen.getByText('Hello, AI!')).toBeInTheDocument();
  });

  it('renders assistant message correctly', () => {
    render(<ChatMessage role="assistant" content="Hello! How can I help you?" />);

    expect(screen.getByTestId('chat-message')).toBeInTheDocument();
    expect(screen.getByText('assistant')).toBeInTheDocument();
    expect(screen.getByText('Hello! How can I help you?')).toBeInTheDocument();
  });

  it('applies correct CSS class based on role', () => {
    const { container } = render(<ChatMessage role="user" content="Test" />);

    const messageElement = container.querySelector('.message-user');
    expect(messageElement).toBeInTheDocument();
  });

  it('handles long content', () => {
    const longContent = 'A'.repeat(1000);
    render(<ChatMessage role="user" content={longContent} />);

    expect(screen.getByText(longContent)).toBeInTheDocument();
  });

  it('handles special characters in content', () => {
    const specialContent = '<script>alert("xss")</script>';
    render(<ChatMessage role="user" content={specialContent} />);

    // Content should be escaped and displayed as text
    expect(screen.getByText(specialContent)).toBeInTheDocument();
  });
});
