'use client';

import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { api, Task } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

interface TaskFormProps {
  onTaskAdded: (task: Task) => void;
}

export default function TaskForm({ onTaskAdded }: TaskFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) return;

    setIsSubmitting(true);
    try {
      const newTask = await api.createTask({
        title,
        description
      });

      onTaskAdded(newTask);
      setTitle('');
      setDescription('');
      toast.success('Task deployed successfully', {
        description: `Operational node "${title}" is now active.`
      });
    } catch (error: any) {
      console.error('Error adding task:', error);
      toast.error('Deployment failed', {
        description: error.message || 'Check terminal logs for diagnostic details.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="glass-card rounded-2xl p-8 relative overflow-hidden group">
      {/* Glow Effect */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-primary/10 transition-colors duration-700 pointer-events-none"></div>

      <h2 className="text-2xl font-bold font-heading mb-6 flex items-center gap-3">
        <span className="p-2 rounded-lg bg-primary/10 text-primary">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" /></svg>
        </span>
        New Task
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6 relative z-10">
        <div className="space-y-2">
          <label htmlFor="title" className="text-sm font-medium text-foreground">
            What needs to be done?
          </label>
          <Input
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            placeholder="Task title..."
            className="bg-background/50 border-border focus-visible:ring-primary"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="description" className="text-sm font-medium text-foreground">
            Description (Optional)
          </label>
          <Textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            placeholder="Add details..."
            className="bg-background/50 border-border focus-visible:ring-primary resize-none"
          />
        </div>

        <div className="flex justify-end pt-2">
          <Button
            type="submit"
            size="lg"
            className="rounded-xl shadow-lg shadow-primary/25 font-semibold"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Deploying...
              </>
            ) : (
              <>
                Create Task
                <svg className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}