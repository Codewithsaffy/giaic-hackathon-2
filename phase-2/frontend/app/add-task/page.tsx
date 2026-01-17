'use client';

import { useRouter } from 'next/navigation';
import TaskForm from '@/components/task-form';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function AddTaskPage() {
    const router = useRouter();

    const handleTaskAdded = () => {
        // Redirect back to dashboard after adding
        router.push('/todo');
    };

    return (
        <div className="w-full px-4 py-8 md:px-8 md:py-12 max-w-2xl mx-auto min-h-screen flex flex-col justify-center">
            <div className="w-full">
                <Button
                    variant="ghost"
                    onClick={() => router.back()}
                    className="text-neutral-500 hover:text-white mb-8 md:mb-12 -ml-2 md:-ml-4 flex items-center gap-2 transition-all"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Back to Terminal
                </Button>

                <div className="mb-8 md:mb-12">
                    <h1 className="text-3xl md:text-4xl font-bold font-heading text-white tracking-tighter mb-2">
                        Deploy New Node
                    </h1>
                    <p className="text-neutral-500 font-light text-sm md:text-base">
                        Initialize a new task object within the operational workspace.
                    </p>
                </div>

                <div className="animate-in slide-in-from-bottom-4 duration-700">
                    <TaskForm onTaskAdded={handleTaskAdded} />
                </div>
            </div>
        </div>
    );
}
