import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownProps {
    content: string;
}

export function Markdown({ content }: MarkdownProps) {
    return (
        <div className="markdown-content chat-window-markdown text-sm prose prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
        </div>
    );
}
