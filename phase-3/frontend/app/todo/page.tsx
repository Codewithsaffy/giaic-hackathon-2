import { auth } from '@/lib/auth';
import { headers } from 'next/headers';
import { redirect } from 'next/navigation';
import { tasksApiServer, Task } from '@/lib/api-server';
import TodoList from '@/components/todo-list';

export default async function TodoPage() {
  // Check if user is authenticated
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    redirect('/auth/sign-in');
  }

  // Fetch tasks from the API server-side
  let initialTasks: Task[] = [];
  try {
    initialTasks = await tasksApiServer.getAll(session.user.id);
  } catch (error) {
    console.error('Error fetching tasks:', error);
  }

  return (
    <div className="min-h-screen pt-24 pb-12 px-4 sm:px-6 lg:px-8 bg-background relative z-10">
      <div className="max-w-7xl mx-auto">
        <TodoList initialTasks={initialTasks} />
      </div>
    </div>
  );
}