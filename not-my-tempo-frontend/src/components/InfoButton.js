'use client';

import { useState } from 'react';
import { IoInformationCircleOutline, IoClose } from 'react-icons/io5';
import Image from 'next/image';

export default function InfoButton() {
    const [showInfo, setShowInfo] = useState(false);

    const gestureInfo = [
        {
            gesture: 'Conductor\'s Fist',
            action: 'Pause video',
            image: '/gestures/thumbs-up.png'  // You'll need to add these images to your public folder
        },
        {
            gesture: 'Two-fingered Conducting',
            action: 'Play video',
            image: '/gestures/victory.png'
        },
        {
            gesture: 'Upwards Facing Open Palm',
            action: 'Speed up video',
            image: '/gestures/open-palm.png'
        },
        {
            gesture: 'Downwards Facing Open Palm',
            action: 'Slow down video',
            image: '/gestures/closed-fist.png'
        }
    ];

    return (
        <>
            <button
                onClick={() => setShowInfo(true)}
                className="text-gray-600 hover:text-gray-800 transition-colors"
                aria-label="Gesture Information"
            >
                <IoInformationCircleOutline size={24} />
            </button>
            
            {showInfo && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-2xl font-bold">Gesture Controls Guide</h2>
                            <button 
                                onClick={() => setShowInfo(false)}
                                className="text-gray-500 hover:text-gray-700"
                            >
                                <IoClose size={24} />
                            </button>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {gestureInfo.map((info) => (
                                <div 
                                    key={info.gesture} 
                                    className="border rounded-lg p-4 hover:shadow-lg transition-shadow"
                                >
                                    <div className="aspect-square relative mb-3 bg-gray-100 rounded-lg overflow-hidden">
                                        <Image
                                            src={info.image}
                                            alt={`${info.gesture} gesture`}
                                            fill
                                            className="object-cover"
                                            loading="lazy"
                                        />
                                    </div>
                                    <h3 className="font-semibold text-lg mb-1">{info.gesture}</h3>
                                    <p className="text-gray-600">{info.action}</p>
                                </div>
                            ))}
                        </div>
                        
                        <div className="mt-6 text-sm text-gray-500">
                            <p>Position your hand clearly in view of the camera for best detection results.</p>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
} 