'use client';

import { useState, useEffect } from 'react';
import { api, Task } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { CheckCircle2, Circle, Trash2, Calendar, Clock, Terminal, Sparkles, Search } from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

export default function TodoList({ initialTasks = [] }: { initialTasks?: Task[] }) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [loading, setLoading] = useState(initialTasks.length === 0);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 500);
    return () => clearTimeout(timer);
  }, [search]);

  useEffect(() => {
    fetchTasks();
  }, [debouncedSearch]);

  const fetchTasks = async () => {
    try {
      const data = await api.getTasks({ search: debouncedSearch || undefined });
      setTasks(data);
    } catch (error: any) {
      console.error('Error fetching tasks:', error);
      toast.error('Sync failed', {
        description: 'Could not synchronize with the operational stream.'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTaskAdded = (newTask: Task) => {
    setTasks([newTask, ...tasks]);
  };

  const toggleTaskCompletion = async (id: number) => {
    const taskIndex = tasks.findIndex((t) => t.id === id);
    if (taskIndex === -1) return;

    const originalTask = tasks[taskIndex];
    const newStatus = !originalTask.completed;

    // Optimistic Update
    const updatedTasks = [...tasks];
    updatedTasks[taskIndex] = { ...originalTask, completed: newStatus };
    setTasks(updatedTasks);

    toast.info(newStatus ? 'Node Resolved' : 'Node Reactivated', {
      description: `Status for "${originalTask.title}" has been updated.`
    });

    try {
      const result = await api.toggleTaskComplete(id);
      // Synchronize with server result just in case
      setTasks(prev => prev.map(t => t.id === id ? result : t));
    } catch (error) {
      console.error('Error toggling task:', error);
      // Rollback
      setTasks(prev => prev.map(t => t.id === id ? originalTask : t));
      toast.error('Update failed', {
        description: 'Communication error. Reverting status.'
      });
    }
  };

  const deleteTask = async (id: number) => {
    const taskIndex = tasks.findIndex((t) => t.id === id);
    if (taskIndex === -1) return;

    const originalTasks = [...tasks];
    const taskToDelete = originalTasks[taskIndex];

    // Optimistic Delete
    setTasks(tasks.filter((t) => t.id !== id));

    toast.success('Node Decommissioned', {
      description: `Task "${taskToDelete.title}" removed from workspace.`
    });

    try {
      await api.deleteTask(id);
    } catch (error) {
      console.error('Error deleting task:', error);
      // Rollback
      setTasks(originalTasks);
      toast.error('Purge failed', {
        description: 'Could not delete node. Restoring to workspace.'
      });
    }
  };

  return (
    <div className="w-full px-8 py-10 max-w-7xl mx-auto">
      {/* Dashboard Top Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <span className="badge-best uppercase tracking-tighter">WORKSPACE 01</span>
            <span className="text-neutral-700 text-xs font-mono">ID: 0x7FA2...</span>
          </div>
          <h1 className="text-4xl font-bold font-heading text-white tracking-tighter">
            Operational Dashboard
          </h1>
        </div>

        <div className="flex items-center gap-6 pb-2">
          <div className="flex flex-col items-end">
            <span className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Active nodes</span>
            <span className="text-xl font-bold text-white">{tasks.filter(t => !t.completed).length}</span>
          </div>
          <div className="w-px h-8 bg-neutral-800"></div>
          <div className="flex flex-col items-end">
            <span className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Efficiency</span>
            <span className="text-xl font-bold text-emerald-400">
              {tasks.length > 0 ? Math.round((tasks.filter(t => t.completed).length / tasks.length) * 100) : 0}%
            </span>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-neutral-500 uppercase tracking-[0.2em] flex items-center gap-2">
            <Terminal className="w-4 h-4" />
            Active Task Stream
          </h3>
          <div className="flex items-center gap-4 w-full md:w-auto">
            <div className="relative flex-1 md:w-64">
              <Input
                placeholder="Search tasks..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="bg-neutral-900 border-neutral-800 text-neutral-300 placeholder:text-neutral-600 focus-visible:ring-neutral-700"
              />
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
              <span className="text-[10px] font-medium text-neutral-400">Live Data</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {tasks.length === 0 && !loading ? (
            <div className="col-span-full py-32 flex flex-col items-center justify-center text-center inspiration-card border-dashed">
              <div className="w-16 h-16 rounded-2xl bg-neutral-900 border border-neutral-800 flex items-center justify-center mb-6">
                <Circle className="w-8 h-8 text-neutral-700" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2 tracking-tight">Zero latency detected.</h3>
              <p className="text-neutral-500 max-w-xs font-light">
                The stream is currently empty. Initiate a new task node to begin.
              </p>
            </div>
          ) : (
            tasks.map((task, idx) => (
              <div
                key={task.id}
                className={cn(
                  "inspiration-card p-5 group animate-in slide-in-from-left-4 duration-500",
                  task.completed ? "opacity-50 border-neutral-900" : "hover:border-neutral-600"
                )}
                style={{ animationDelay: `${idx * 50}ms` }}
              >
                <div className="flex items-start gap-4">
                  <button
                    onClick={() => toggleTaskCompletion(task.id)}
                    className={cn(
                      "flex-shrink-0 w-8 h-8 rounded-lg border flex items-center justify-center mt-0.5 transition-all duration-300",
                      task.completed
                        ? "bg-white border-white text-black"
                        : "bg-neutral-900 border-neutral-800 text-neutral-600 hover:border-neutral-500"
                    )}
                  >
                    {task.completed ? <CheckCircle2 className="w-4 h-4" /> : <Circle className="w-4 h-4" />}
                  </button>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        {task.completed ? <span className="badge-best">RESOLVED</span> : <span className="badge-new">ACTIVE</span>}
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => deleteTask(task.id)}
                        className="w-6 h-6 rounded text-neutral-600 hover:text-red-500 hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </Button>
                    </div>

                    <h3 className={cn(
                      "text-base font-bold transition-all duration-300 leading-snug",
                      task.completed ? "text-neutral-500 line-through" : "text-white"
                    )}>
                      {task.title}
                    </h3>

                    {task.description && (
                      <p className="mt-2 text-xs text-neutral-500 line-clamp-2 font-light leading-relaxed">
                        {task.description}
                      </p>
                    )}

                    <div className="mt-3 flex flex-wrap gap-2">
                      {task.priority && (
                        <Badge className={cn(
                          "text-[9px] font-bold px-2 py-0",
                          task.priority === 1 ? "bg-red-500/10 text-red-500 border-red-500/20" :
                            task.priority === 2 ? "bg-orange-500/10 text-orange-500 border-orange-500/20" :
                              task.priority === 4 ? "bg-blue-500/10 text-blue-500 border-blue-500/20" :
                                task.priority === 5 ? "bg-neutral-500/10 text-neutral-500 border-neutral-500/20" :
                                  "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
                        )}>
                          P{task.priority}
                        </Badge>
                      )}
                      {task.tags?.split(',').map((tag, i) => (
                        <Badge key={i} variant="outline" className="text-[9px] font-medium border-neutral-800 text-neutral-400">
                          {tag.trim()}
                        </Badge>
                      ))}
                    </div>

                    <div className="mt-4 pt-3 border-t border-neutral-800/50 flex items-center justify-between">
                      <div className="flex items-center gap-3 text-[9px] text-neutral-600 font-bold uppercase tracking-widest">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(task.created_at).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}
                        </div>
                        {task.due_date && (
                          <div className="flex items-center gap-1 text-amber-500/80">
                            <Calendar className="w-3 h-3" />
                            {new Date(task.due_date).toLocaleDateString()}
                          </div>
                        )}
                      </div>
                      <span className="text-[9px] text-neutral-700 font-mono">
                        #{task.id}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}