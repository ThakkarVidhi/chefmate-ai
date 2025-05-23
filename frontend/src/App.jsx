import Chatbot from '@/components/Chatbot';
import logo from '@/assets/images/logo.svg';

function App() {

  return (
    <div className='flex flex-col min-h-full w-full max-w-3xl mx-auto px-4'>
      <header className='sticky top-0 shrink-0 z-20 bg-white'>
        <div className='flex justify-center items-center py-4'>
          <img src={logo} className='h-24 sm:h-28 object-contain' alt='logo' />
        </div>
      </header>
      <Chatbot />
    </div>
  );
}

export default App;